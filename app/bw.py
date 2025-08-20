import bw2data as bd
import bw2calc as bc
from bw2data.backends import ActivityDataset as AD


def list_projects() -> list[str]:
    """List all available Brightway2 projects."""
    return [proj.name for proj in bd.projects]

def set_current_project(project_name: str) -> None:
    """Set the current Brightway2 project."""
    bd.projects.set_current(project_name)

def list_databases() -> list[str]:
    """List all available Brightway2 projects."""
    return list(bd.databases)

def list_processes(db_name: str):
    """List all processes in a given Brightway2 database."""
    db = bd.Database(db_name)
    return list((act for act in db))

def search_db(db, term: str) :
    return bd.Database(db).search(term)

def filter_results(db, name="", product="", location=""):
    """Filter results based on name, product, and location."""
    return [act for act in bd.Database(db)
            if name.lower() in act.get("name").lower() and
            product.lower() in act.get("reference product", "").lower() and
            location.lower() in act.get("location", "").lower()]
    
def query_distinct_process_names(db):
    query = AD.select(AD.name).where(AD.database == db).distinct()
    return [entry.name for entry in query]