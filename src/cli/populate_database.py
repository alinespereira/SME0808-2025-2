import logging
import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import click
import pandas as pd
from sqlmodel import Session, select, text

from tsa import Logger, settings
from tsa.database.connector import Connector
from tsa.database.models import City, Observation, Region, State, Station

logger = Logger(__name__, level=logging.INFO)

META_ROWS = 8

REGION_NAMES = {
    "N": "Norte",
    "NE": "Nordeste",
    "CO": "Centro-Oeste",
    "SE": "Sudeste",
    "S": "Sul",
}

STATE_NAMES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

META_MAP = {
    "regiao": "region_code",
    "uf": "state_code",
    "estacao": "station_name",
    "codigo_wmo": "station_code",
    "latitude": "latitude",
    "longitude": "longitude",
    "altitude": "altitude",
    "data_de_fundacao": "start_date",
}

OBSERVATION_MAP = {
    "precipitacao_total_horario_mm": "precipitation",
    "pressao_atmosferica_ao_nivel_da_estacao_horaria_mb": "atmospheric_pressure",
    "pressao_atmosferica_max_na_hora_ant_aut_mb": "prev_max_pressure",
    "pressao_atmosferica_min_na_hora_ant_aut_mb": "prev_min_pressure",
    "radiacao_global_kj_m2": "global_radiation",
    "temperatura_do_ar_bulbo_seco_horaria_c": "air_temperature",
    "temperatura_do_ponto_de_orvalho_c": "dew_point_temperature",
    "temperatura_maxima_na_hora_ant_aut_c": "max_temperature",
    "temperatura_minima_na_hora_ant_aut_c": "min_temperature",
    "temperatura_orvalho_max_na_hora_ant_aut_c": "max_dew_point_temperature",
    "temperatura_orvalho_min_na_hora_ant_aut_c": "min_dew_point_temperature",
    "umidade_rel_max_na_hora_ant_aut": "max_relative_humidity",
    "umidade_rel_min_na_hora_ant_aut": "min_relative_humidity",
    "umidade_relativa_do_ar_horaria": "relative_humidity",
    "vento_direcao_horaria_gr_gr": "wind_direction",
    "vento_rajada_maxima_m_s": "max_wind_gust",
    "vento_velocidade_horaria_m_s": "wind_speed",
}


@dataclass(frozen=True)
class StationMetadata:
    region_code: str
    state_code: str
    station_name: str
    station_code: str
    latitude: float
    longitude: float
    altitude: float
    start_date: str | None
    city_name: str | None


def normalize_token(value: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    normalized = normalized.lower()
    normalized = normalized.removesuffix("(yyyy-mm-dd)")
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")


def parse_metadata(csv_path: Path) -> StationMetadata:
    values: dict[str, str] = {}
    with csv_path.open(encoding="latin-1") as fp:
        for _ in range(META_ROWS):
            line = fp.readline()
            if not line:
                break
            parts = line.strip().split(";", maxsplit=1)
            if len(parts) != 2:
                continue

            label, raw_value = parts
            label = normalize_token(label.rstrip(":"))
            if label in META_MAP:
                values[META_MAP[label]] = raw_value.strip()

    station_code = values.get("station_code")
    if not station_code:
        raise ValueError(f"Código da estação não encontrado em {csv_path.name}")

    return StationMetadata(
        region_code=values.get("region_code", "").upper(),
        state_code=values.get("state_code", "").upper(),
        station_name=values.get("station_name", "").title(),
        station_code=station_code.upper(),
        latitude=_to_float(values.get("latitude")),
        longitude=_to_float(values.get("longitude")),
        altitude=_to_float(values.get("altitude")),
        start_date=values.get("start_date"),
        city_name=infer_city_name(csv_path),
    )


def infer_city_name(csv_path: Path) -> str | None:
    parts = csv_path.stem.split("_")
    if len(parts) < 6:
        return None
    city_parts = parts[4:5]
    if not city_parts:
        return None
    city = " ".join(part.replace("-", " ") for part in city_parts).strip()
    return city.title() if city else None


def _to_float(raw: str) -> float:
    raw = raw.replace(",", ".")
    return float(raw)


def load_observations(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(  # type: ignore[call-overload]
        csv_path,
        sep=";",
        skiprows=META_ROWS,
        encoding="latin-1",
        decimal=",",
        na_values=["-9999", -9999],
        engine="python",
    )
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False, na=False)]
    normalized_cols = [normalize_token(str(col)) for col in df.columns]
    df.columns = normalized_cols
    df = df.dropna(how="all", subset=OBSERVATION_MAP)

    required = {"data", "hora_utc"}
    if not required.issubset(set(df.columns)):
        missing = required - set(df.columns)
        raise ValueError(
            f"Colunas obrigatórias ausentes em {csv_path.name}: {missing}"
        )

    df = df.assign(
        datetime=pd.to_datetime(
            df["data"] + " " + df["hora_utc"],
            format="%Y-%m-%d %H:%M",
            errors="coerce",
        )
    )
    df = df.dropna(subset=["datetime"])

    rename_map = {
        source: target
        for source, target in OBSERVATION_MAP.items()
        if source in df.columns
    }
    df = df.rename(columns=rename_map)
    return df[["datetime", *rename_map.values()]]


def ensure_region(session: Session, code: str) -> Region:
    region = session.exec(select(Region).where(Region.code == code)).first()
    if region:
        return region
    region = Region(code=code, name=REGION_NAMES.get(code, code))
    session.add(region)
    session.commit()
    session.refresh(region)
    return region


def ensure_state(session: Session, code: str, region_id: int) -> State:
    state = session.exec(select(State).where(State.code == code)).first()
    if state:
        if state.region_id != region_id:
            state.region_id = region_id
            session.add(state)
            session.commit()
            session.refresh(state)
        return state
    state = State(
        code=code,
        name=STATE_NAMES.get(code, code),
        region_id=region_id,
    )
    session.add(state)
    session.commit()
    session.refresh(state)
    return state


def ensure_city(session: Session, name: str, state_id: int) -> City:
    statement = select(City).where(City.name == name, City.state_id == state_id)
    logger.debug(f"Ensuring city with statement: {statement}")
    city = session.exec(statement).first()
    logger.debug(f"City found: {city = }")
    if city:
        return city
    city = City(name=name, state_id=state_id)
    session.add(city)
    session.commit()
    session.refresh(city)
    return city


def ensure_station(
    session: Session, metadata: StationMetadata, state_id: int, city_id: int
) -> Station:
    station = session.exec(
        select(Station).where(Station.code == metadata.station_code)
    ).first()
    if station:
        station.latitude = metadata.latitude
        station.longitude = metadata.longitude
        station.altitude = metadata.altitude
        station.city_id = city_id
        station.state_id = state_id
        session.add(station)
        session.commit()
        session.refresh(station)
        logger.debug(f"Updated station {station} in database.")
        return station

    station = Station(
        code=metadata.station_code,
        latitude=metadata.latitude,
        longitude=metadata.longitude,
        altitude=metadata.altitude,
        city_id=city_id,
        state_id=state_id,
    )
    session.add(station)
    session.commit()
    session.refresh(station)
    return station


def to_float(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return float(value)


def iter_observations(
    rows: pd.DataFrame, station_id: int
) -> Iterable[Observation]:
    for record in rows.to_dict(orient="records"):
        yield Observation(
            station_id=station_id,
            datetime=record["datetime"].to_pydatetime(),
            precipitation=to_float(record.get("precipitation")),
            atmospheric_pressure=to_float(record.get("atmospheric_pressure")),
            prev_max_pressure=to_float(record.get("prev_max_pressure")),
            prev_min_pressure=to_float(record.get("prev_min_pressure")),
            global_radiation=to_float(record.get("global_radiation")),
            air_temperature=to_float(record.get("air_temperature")),
            dew_point_temperature=to_float(record.get("dew_point_temperature")),
            max_temperature=to_float(record.get("max_temperature")),
            min_temperature=to_float(record.get("min_temperature")),
            max_dew_point_temperature=to_float(
                record.get("max_dew_point_temperature")
            ),
            min_dew_point_temperature=to_float(
                record.get("min_dew_point_temperature")
            ),
            max_relative_humidity=to_float(record.get("max_relative_humidity")),
            min_relative_humidity=to_float(record.get("min_relative_humidity")),
            relative_humidity=to_float(record.get("relative_humidity")),
            wind_direction=to_float(record.get("wind_direction")),
            max_wind_gust=to_float(record.get("max_wind_gust")),
            wind_speed=to_float(record.get("wind_speed")),
        )


@click.command()
@click.option(
    "--data-dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=settings.data_path,
    show_default=True,
    help="Diretório com os arquivos CSV do INMET.",
)
@click.option(
    "--pattern",
    default="*.CSV",
    show_default=True,
    help="Padrão glob utilizado para selecionar os arquivos.",
)
@click.option(
    "--truncate/--no-truncate",
    default=False,
    show_default=True,
    help="Trunca as tabelas antes de popular o banco de dados.",
)
def main(data_dir: Path, pattern: str, truncate: bool = False) -> None:
    """Carrega os CSVs e popula todas as tabelas do banco."""
    csv_files = sorted(data_dir.glob(pattern))
    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado em {data_dir} usando padrão '{pattern}'."
        )

    connector = Connector(settings=settings.db)

    with Session(connector.engine) as session:
        if truncate:
            logger.info("Truncando tabelas...")
            for table in [Observation, Station, City, State, Region]:
                qualified: str = table.__table__.fullname  # type: ignore[attr-defined]
                session.exec(  # type: ignore[call-overload]
                    text(f"TRUNCATE TABLE {qualified} RESTART IDENTITY CASCADE")
                )
            session.commit()
        for csv_path in csv_files:
            logger.info(f"Processando {csv_path.name}...")
            try:
                metadata = parse_metadata(csv_path)
                logger.debug("Parsed metadata")
                logger.debug(f"{metadata = }")
                region = ensure_region(session, metadata.region_code)
                state = ensure_state(session, metadata.state_code, region.id)
                city_name = metadata.city_name or metadata.station_name
                city = ensure_city(session, city_name, state.id)
                station = ensure_station(session, metadata, state.id, city.id)

                observations_df = load_observations(csv_path)
                for chunk in _chunked(
                    iter_observations(observations_df, station.id), size=500
                ):
                    session.add_all(chunk)
                    session.commit()
            except ValueError as e:
                logger.error(f"Erro ao processar {csv_path.name}: {e}")
                continue

    logger.info("Banco populado com sucesso.")


def _chunked(
    iterable: Iterable[Observation], size: int
) -> Iterable[list[Observation]]:
    chunk: list[Observation] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
