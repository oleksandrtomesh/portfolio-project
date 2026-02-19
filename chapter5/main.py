from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

import crud, schemas
from database import SessionLocal

api_description = """
This API provides read-only access to info from the SportsWorldCentral
(SWC) Fantasy Football API.
The endpoints are grouped into the following categories:

## Analytics
Get information about the health of the API and counts of leagues, teams,
and players.

## Player
You can get a list of NFL players, or search for an individual player by
player_id.

## Scoring
You can get a list of NFL player performances, including the fantasy points
they scored using SWC league scoring.

## Membership
Get information about all the SWC fantasy football leagues and the teams in them.
"""

app = FastAPI(
    description=api_description,
    title="Sports World Central (SWC) Fantasy Football API",
    version="0.1"
)

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=['analytics'])
async def root():
    return {"message": "API health check successful"}


@app.get("/v0/players/", 
        response_model=list[schemas.Player],
        summary="Get players using query parameters to filter results",
        description="""You can use query parameters to filter the results. For example, you can
        search for players with a minimum last changed date, or search for players by first name or last name.
        ex. /v0/players?first_name=Tom&last_name=Brady&minimum_last_changed_date=2024-01-01""",
        response_description="A list of NFL players",
        operation_id="v0_get_players",
        tags=['player'])
def read_players(skip: int=Query(0, description="Number of records to skip for pagination"),
                limit: int=Query(100, description="The number of records to return after the skipped records."),
                minimum_last_changed_date: date=Query(None, description="""The minimum date of
                change that you want to return records. Exclude any records changed before
                this."""),
                first_name: str=Query(None, description="The first name of the player you want to search for"),
                last_name: str=Query(None, description="The last name of the player you want to search for"),
                db: Session=Depends(get_db)):
    players = crud.get_players(db,
                skip=skip,
                limit=limit,
                min_last_changed_date=minimum_last_changed_date,
                first_name=first_name,
                last_name=last_name)
    return players


@app.get("/v0/players/{player_id}",
        response_model=schemas.Player,
        summary="Get one player using the Player ID, which is internal to SWC",
        description="""If you have an SWC Player ID of a player from another API
        call such as v0_get_players, you can call this API
        using the player ID
        ex. /v0/players/1234""",
        response_description="One NFL player",
        operation_id="v0_get_players_by_player_id",
        tags=['player'])
def read_player(player_id: int,
            db: Session = Depends(get_db)):
    player = crud.get_player(db,
                            player_id=player_id)
    if player is None:
        raise HTTPException(status_code=404,
                            detail="Player not found")
    return player


@app.get("/v0/performances/",
        response_model=list[schemas.Performance],
        summary="Get player performances using query parameters to filter results",
        description="""You can use query parameters to filter the results. For example, you can
        search for performances with a minimum last changed date, or search for performances by player_id.
        ex. /v0/performances?player_id=1234&minimum_last_changed_date=2024-01-01""",
        response_description="A list of NFL player performances",
        operation_id="v0_get_performances",
        tags=['scoring'])
def read_performances(skip: int = Query(0, description="Number of records to skip for pagination"),
            limit: int = Query(100, description="The number of records to return after the skipped records."),
            minimum_last_changed_date: date = Query(None, description="""The minimum date of
                change that you want to return records. Exclude any records changed before
                this."""),
            db: Session = Depends(get_db)):
    performances = crud.get_performance(db,
            skip=skip,
            limit=limit,
            min_last_changed_date=minimum_last_changed_date)
    return performances


@app.get("/v0/leagues/{league_id}",
        response_model=schemas.League,
        summary="Get one league using the League ID, which is internal to SWC",
        description="""If you have an SWC League ID of a league from another API
        call such as v0_get_leagues, you can call this API
        using the league ID
        ex. /v0/leagues/1234""",
        response_description="One NFL league",
        operation_id="v0_get_league_by_league_id",
        tags=['membership'])
def read_league(league_id: int,db: Session = Depends(get_db)):
    league = crud.get_league(db, league_id = league_id)
    if league is None:
        raise HTTPException(status_code=404, 
                        detail="League not found")
    return league


@app.get("/v0/leagues/",
        response_model=list[schemas.League],
        summary="Get leagues using query parameters to filter results",
        description="""You can use query parameters to filter the results. For example, you can
        search for leagues with a minimum last changed date, or search for leagues by name.
        ex. /v0/leagues?league_name=SuperBowl&minimum_last_changed_date=2024-01-01""",
        response_description="A list of NFL leagues",
        operation_id="v0_get_leagues",
        tags=['membership'])
def read_leagues(skip: int = Query(0, description="Number of records to skip for pagination"),
                limit: int = Query(100, description="The number of records to return after the skipped records."),
                minimum_last_changed_date: date = Query(None, description="""The minimum date of
                    change that you want to return records. Exclude any records changed before
                    this."""),
                league_name: str = Query(None, description="The name of the league you want to search for"),
                db: Session = Depends(get_db)):
    leagues = crud.get_leagues(db,
                skip=skip,
                limit=limit,
                min_last_changed_date=minimum_last_changed_date,
                league_name=league_name)
    return leagues


@app.get("/v0/teams/",
        response_model=list[schemas.Team],
        summary="Get teams using query parameters to filter results",
        description="""You can use query parameters to filter the results. For example, you can
        search for teams with a minimum last changed date, or search for teams by name or league_id.
        ex. /v0/teams?team_name=NewEnglandPatriots&minimum_last_changed_date=2024-01-01""",
        response_description="A list of NFL teams",
        operation_id="v0_get_teams",
        tags=['membership'])
def read_teams(skip: int=Query(0, description="Number of records to skip for pagination"),
            limit: int = Query(100, description="The number of records to return after the skipped records."),
            minimum_last_changed_date: date = Query(None, description="""The minimum date of
                    change that you want to return records. Exclude any records changed before
                    this."""),
            team_name: str = Query(None, description="The name of the team you want to search for"),
            league_id: int = Query(None, description="The league ID of the team you want to search for"),
            db: Session = Depends(get_db)):
    teams = crud.get_teams(
                    db,
                    skip=skip,
                    limit=limit,
                    min_last_changed_date=minimum_last_changed_date,
                    team_name=team_name,
                    league_id=league_id,
                )
    return teams

@app.get("/v0/counts",
        response_model=schemas.Counts,
        summary="Get counts of leagues, teams, and players",
        description="""You can get the counts of leagues, teams, and players in the database.
        ex. /v0/counts""",
        response_description="Counts of leagues, teams, and players",
        operation_id="v0_get_counts",
        tags=['analytics'])
def get_count(db: Session = Depends(get_db)):
    counts = schemas.Counts(
            league_count=crud.get_league_count(db),
            team_count=crud.get_team_count(db),
            player_count=crud.get_player_count(db)
        )
    return counts