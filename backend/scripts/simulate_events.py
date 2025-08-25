import argparse, random, os, sys
from datetime import timedelta

# Make backend modules importable when running as a script
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import utcnow  # noqa: E402
import schemas  # noqa: E402
from main import ingest_run, get_db  # noqa: E402

def main():
    parser = argparse.ArgumentParser(description="Simulate CI/CD pipeline runs")
    parser.add_argument("--pipelines", type=str, default="web,api", help="Comma-separated pipeline names")
    parser.add_argument("--count", type=int, default=20, help="Number of runs to create")
    parser.add_argument("--fail-rate", type=float, default=0.25, help="Probability of failure per run")
    args = parser.parse_args()

    pipelines = [p.strip() for p in args.pipelines.split(",") if p.strip()]
    created = 0

    for db in get_db():
        for _ in range(args.count):
            name = random.choice(pipelines)
            status = schemas.RunStatus.failure if random.random() < args.fail_rate else schemas.RunStatus.success
            start = utcnow() - timedelta(minutes=random.randint(0, 60))
            dur = random.randint(30, 900)
            finish = start + timedelta(seconds=dur)
            ingest_run(
                schemas.RunIn(
                    pipeline=name, status=status, started_at=start, finished_at=finish, duration_sec=dur,
                    branch="main", commit=f"{random.randint(0, 16**7):07x}", triggered_by="sim-script"
                ),
                db
            )
            created += 1
        break

    print(f"Created {created} simulated runs for pipelines: {', '.join(pipelines)}")

if __name__ == "__main__":
    main()
