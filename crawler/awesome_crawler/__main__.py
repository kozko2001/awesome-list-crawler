import logging
from datetime import datetime
from pathlib import Path

import click

from awesome_crawler.find_awesome_repos import find_repos
from awesome_crawler.output import generate_json
from awesome_crawler.process import crawl_awesome, AwesomeList
from awesome_crawler.delta import get_last
from awesome_crawler.serialize import deserialize
from awesome_crawler.sampling import filter_repositories_by_activity, log_sampling_statistics


def get_repos_from_data(data_str: str = None):
    """Get repository list from provided data or S3 as fallback"""
    try:
        if data_str:
            print("🔄 Extracting repository list from provided data...")
            output = deserialize(data_str)
        else:
            print("🔄 Extracting repository list from S3 data...")
            s3_data = get_last()
            output = deserialize(s3_data)
        
        repos = []
        for list_data in output.lists:
            repo = AwesomeList(list_data.name, list_data.source, list_data.description)
            repos.append(repo)
        print(f"✅ Extracted {len(repos)} repositories from data")
        return repos
    except Exception as e:
        print(f"❌ Failed to get repos from data: {e}")
        print("🔄 Falling back to discovery...")
        logging.error(f"Failed to get repos from data: {e}")
        logging.info("Falling back to discovery")
        return find_repos()


def should_run_discovery():
    """Check if today is Monday (discovery day)"""
    return datetime.now().weekday() == 0  # Monday is 0


@click.command()
@click.option("--logs/--no-logs", default=False)
@click.option("--write-s3/--no-write-s3", default=True)
@click.option("--force-discovery/--no-force-discovery", default=False)
@click.option("--probabilistic-sampling/--no-probabilistic-sampling", default=True)
@click.option("--data-file", type=click.Path(exists=True), help="Use local data file instead of S3 for incremental processing")
@click.option("--single-repo", help="Skip discovery and process only this repository URL")
def main(logs: bool, write_s3: bool, force_discovery: bool, probabilistic_sampling: bool, data_file: str, single_repo: str):
    print(f"🚀 Starting awesome crawler...")
    print(f"📋 Configuration: logs={logs}, write_s3={write_s3}, force_discovery={force_discovery}, probabilistic_sampling={probabilistic_sampling}, data_file={data_file}, single_repo={single_repo}")
    
    if logs:
        logging.basicConfig(filename="crawler.log", level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    # Get data for probabilistic sampling and incremental processing
    s3_data = None
    s3_data_str = None
    
    try:
        if data_file:
            print(f"🔍 Loading data from local file: {data_file}")
            with open(data_file, 'r') as f:
                s3_data_str = f.read()
            print("✅ Local data loaded successfully")
            logging.info(f"Local data loaded from {data_file}")
        elif probabilistic_sampling:
            print("🔍 Loading S3 data for probabilistic sampling...")
            s3_data_str = get_last()
            print("✅ S3 data loaded successfully")
            logging.info("S3 data loaded for probabilistic sampling")
        else:
            print("📝 No data file provided and probabilistic sampling disabled, skipping data load")
            logging.info("No data loading - no file provided and probabilistic sampling disabled")
        
        if s3_data_str:
            print("🔄 Parsing data...")
            s3_data = deserialize(s3_data_str)
            print("✅ Data parsed successfully")
    except Exception as e:
        print(f"⚠️  Could not load data: {e}")
        logging.warning(f"Could not load data: {e}")

    # Determine whether to run discovery, use S3 data, or process single repo
    if single_repo:
        print(f"🎯 Processing single repository: {single_repo}")
        logging.info(f"Processing single repository: {single_repo}")
        list_of_awesome_projects = [AwesomeList("single-repo", single_repo, "Single repository for testing")]
    elif force_discovery or should_run_discovery():
        print("🔍 Running repository discovery (Monday or forced)...")
        logging.info("Running repository discovery (Monday or forced)")
        list_of_awesome_projects = find_repos()
    else:
        print("📂 Using repository list from data (non-Monday)...")
        logging.info("Using repository list from data (non-Monday)")
        list_of_awesome_projects = get_repos_from_data(s3_data_str)
    
    print(f"📊 Found {len(list_of_awesome_projects)} repositories")
    
    # Apply probabilistic sampling based on repository activity
    if probabilistic_sampling and s3_data:
        print("🎲 Applying probabilistic sampling based on repository activity...")
        logging.info("Applying probabilistic sampling based on repository activity")
        log_sampling_statistics(list_of_awesome_projects, s3_data)
        list_of_awesome_projects = filter_repositories_by_activity(list_of_awesome_projects, s3_data)
    
    print(f"⚡ Processing {len(list_of_awesome_projects)} repositories...")
    logging.info(f"Processing {len(list_of_awesome_projects)} repositories")
    items = crawl_awesome(list_of_awesome_projects, None, s3_data)
    items_flatten = [x for i in items for x in i]

    dest = None if write_s3 else Path("./output.json")
    print("💾 Generating and saving output...")
    
    # Pass the local data for delta calculation if available
    old_data_str = None
    if data_file:
        with open(data_file, 'r') as f:
            old_data_str = f.read()
    
    generate_json(items_flatten, dest, old_data_str)
    print("🎉 Crawler execution completed!")


if __name__ == "__main__":
    main()
