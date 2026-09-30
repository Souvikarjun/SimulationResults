import json
from pathlib import Path
from statistics import mean


TIMING_FIELDS = (
    "execution_time_us",
    "key_generation_time_us",
    "encryption_time_us",
    "decryption_time_us",
    "signing_time_us",
    "verification_us",
)


def main() -> None:
    folder = Path(__file__).resolve().parent
    input_path = folder / "ML_KEM_512.json"
    output_path = folder / "ML_KEM_512_average_results.json"

    with input_path.open("r", encoding="utf-8") as source_file:
        records = json.load(source_file)

    per_run = []
    values_by_timing = {timing: [] for timing in TIMING_FIELDS}

    for run_number, record in enumerate(records, start=1):
        result = record.get("result") or {}
        vehicles = record.get("vehicles", result.get("total_vehicles"))
        if not vehicles:
            continue

        totals = {timing: result.get(timing) for timing in TIMING_FIELDS}
        totals["signing_time_us"] = totals["signing_time_us"] or record.get("signing_us")
        totals["verification_us"] = totals["verification_us"] or record.get("verification_us")
        per_vehicle = {
            timing: total / vehicles if total is not None else None
            for timing, total in totals.items()
        }

        for timing, value in per_vehicle.items():
            if value is not None:
                values_by_timing[timing].append(value)

        per_run.append({
            "run_number": run_number,
            "vehicles": vehicles,
            "duration_seconds": record.get("duration_seconds"),
            "timing_totals_us": totals,
            "timing_per_vehicle_us": per_vehicle,
            "generated_messages": record.get("generated"),
            "delivered_messages": record.get("delivered"),
            "verified_messages": record.get("verified"),
            "bytes_on_wire": record.get("bytes_on_wire"),
            "memory_usage_bytes": result.get("memory_usage_bytes"),
        })

    averages = {
        timing: {
            "average_per_vehicle_us": sum(values) / len(values) if values else None,
            "runs_used": len(values),
        }
        for timing, values in values_by_timing.items()
    }
    report = {
        "input_file": input_path.name,
        "calculation": "Each run's total timing is divided by its vehicle count; averages are across runs with available data.",
        "average_per_vehicle": averages,
        "runs": per_run,
    }

    with output_path.open("w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2)
        report_file.write("\n")

    print(f"Results saved to {output_path.name}")


if __name__ == "__main__":
    main()