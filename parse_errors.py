import xml.etree.ElementTree as ET  # noqa: S314   # safe use in offline parsing of test results


def parse_failures() -> None:
    # return type is None since this is a standalone utility

    try:
        tree = ET.parse("test_results.xml")  # noqa: S314
        root = tree.getroot()

        with open("test_results.txt", "w", encoding="utf-8") as f:
            failure_count = 0

            for testcase in root.iter("testcase"):
                # Look for failure or error tags inside the testcase
                failure = testcase.find("failure")
                error = testcase.find("error")

                issue = failure if failure is not None else error

                if issue is not None:
                    failure_count += 1
                    file_path = testcase.get("file")
                    test_name = testcase.get("name")
                    error_msg = issue.get("message")
                    # Get the detailed traceback text
                    traceback = issue.text if issue.text else "No traceback available"

                    f.write(f"--- FAILURE #{failure_count} ---\n")
                    f.write(f"FILE: {file_path}\n")
                    f.write(f"TEST: {test_name}\n")
                    f.write(f"MESSAGE: {error_msg}\n")
                    f.write(f"DETAILS:\n{traceback.strip()}\n")
                    f.write("\n" + "=" * 40 + "\n\n")

            print(f"Done! Found {failure_count} failures. Saved to 'test_results.txt'.")  # noqa: T201

    except FileNotFoundError:
        print("Error: Could not find 'test_results.xml'. Did the tests finish running?")  # noqa: T201
    except Exception as e:  # noqa: BLE001,S314
        print(f"An error occurred: {e}")  # noqa: T201


if __name__ == "__main__":
    parse_failures()
