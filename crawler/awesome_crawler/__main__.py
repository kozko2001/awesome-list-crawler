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


def get_repos_from_s3():
    """Get repository list from S3 data instead of running discovery"""
    try:
        s3_data = get_last()
        print("🔄 Extracting repository list from S3 data...")
        output = deserialize(s3_data)
        repos = []
        for list_data in output.lists:
            repo = AwesomeList(list_data.name, list_data.source, list_data.description)
            repos.append(repo)
        print(f"✅ Extracted {len(repos)} repositories from S3 data")
        return repos
    except Exception as e:
        print(f"❌ Failed to get repos from S3: {e}")
        print("🔄 Falling back to discovery...")
        logging.error(f"Failed to get repos from S3: {e}")
        logging.info("Falling back to discovery")
        return find_repos()


def should_run_discovery():
    """Check if today is Monday (discovery day)"""
    return datetime.now().weekday() == 0  # Monday is 0


@click.command()
@click.option("--all/--no-all", default=False)
@click.option("--logs/--no-logs", default=False)
@click.option("--write-s3/--no-write-s3", default=True)
@click.option("--force-discovery/--no-force-discovery", default=False)
@click.option("--probabilistic-sampling/--no-probabilistic-sampling", default=True)
def main(all: bool, logs: bool, write_s3: bool, force_discovery: bool, probabilistic_sampling: bool):
    print(f"🚀 Starting awesome crawler...")
    print(f"📋 Configuration: logs={logs}, all={all}, write_s3={write_s3}, force_discovery={force_discovery}, probabilistic_sampling={probabilistic_sampling}")
    
    if logs:
        logging.basicConfig(filename="crawler.log", level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    # Get S3 data for probabilistic sampling (even on discovery days)
    s3_data = None
    if probabilistic_sampling:
        try:
            print("🔍 Loading S3 data for probabilistic sampling...")
            s3_data_str = get_last()
            print("🔄 Parsing S3 data...")
            s3_data = deserialize(s3_data_str)
            print("✅ S3 data loaded successfully for probabilistic sampling")
            logging.info("S3 data loaded for probabilistic sampling")
        except Exception as e:
            print(f"⚠️  Could not load S3 data for sampling: {e}")
            logging.warning(f"Could not load S3 data for sampling: {e}")

    # Determine whether to run discovery or use S3 data
    if force_discovery or should_run_discovery():
        print("🔍 Running repository discovery (Monday or forced)...")
        logging.info("Running repository discovery (Monday or forced)")
        list_of_awesome_projects = find_repos()
    else:
        print("📂 Using repository list from S3 data (non-Monday)...")
        logging.info("Using repository list from S3 data (non-Monday)")
        list_of_awesome_projects = get_repos_from_s3()
    
    print(f"📊 Found {len(list_of_awesome_projects)} repositories")
    
    # Apply probabilistic sampling based on repository activity
    if probabilistic_sampling and s3_data:
        print("🎲 Applying probabilistic sampling based on repository activity...")
        logging.info("Applying probabilistic sampling based on repository activity")
        log_sampling_statistics(list_of_awesome_projects, s3_data)
        list_of_awesome_projects = filter_repositories_by_activity(list_of_awesome_projects, s3_data)
    
    print(f"⚡ Processing {len(list_of_awesome_projects)} repositories...")
    logging.info(f"Processing {len(list_of_awesome_projects)} repositories")
    limit_commits = None if all else 10
    items = crawl_awesome(list_of_awesome_projects, limit_commits)
    items_flatten = [x for i in items for x in i]

    dest = None if write_s3 else Path("./output.json")
    print("💾 Generating and saving output...")
    generate_json(items_flatten, dest)
    print("🎉 Crawler execution completed!")


if __name__ == "__main__":
    main()
