import ROOT
import argparse


def merge_histograms(input_filename, output_filename, hist_names, folder):
    """
    Merges all cycles of specified histograms from a ROOT file and saves them to a new file.

    Args:
        input_filename (str): The path to the input ROOT file.
        output_filename (str): The path to the output ROOT file.
        hist_names (list): List of histogram names to merge.
    """

    input_file = ROOT.TFile(input_filename, "READ")
    output_file = ROOT.TFile(output_filename, "RECREATE")

    # Loop over each histogram name
    for hist_name in hist_names:
        # Retrieve all cycles for the histogram
        hist_list = []
        cycle_number = 1
        while True:
            hist = input_file.Get(f"{folder}/{hist_name};{cycle_number}")
            if not hist:
                break
            hist.SetDirectory(0)
            hist_list.append(hist)
            cycle_number += 1

        # If no histograms were found, skip to the next
        if len(hist_list) == 0:
            raise RuntimeError(f"Warning: No histograms found for {hist_name} in {input_filename}.")

        # Merge all cycles into the first histogram
        merged_hist = hist_list[0].Clone()
        for h in hist_list[1:]:
            merged_hist.Add(h)

        # Preserve the original histogram name
        merged_hist.SetName(hist_name)

        # Write the merged histogram to the output file
        output_file.cd()
        merged_hist.Write()

        print(f"Merged and saved histogram '{hist_name}' with {len(hist_list)} cycles.")

    # Close the files
    input_file.Close()
    output_file.Close()
    print(f"All histograms saved to {output_filename}.")


def main():
    parser = argparse.ArgumentParser(description="Merge all cycles of specified histograms")
    parser.add_argument("-i", "--input", dest="input_filename", default="./histograms.root", type=str)
    parser.add_argument("-o", "--output", dest="output_filename", default="./hists_nevents.root", type=str)
    args = parser.parse_args()

    hist_names = ["nTotalEvents", "nTotalWeightedEvents", "nFilteredvents", "nFilteredventsWeighted"]
    folder = "nanoFilter"

    merge_histograms(
        input_filename=args.input_filename,
        output_filename=args.output_filename,
        hist_names=hist_names,
        folder=folder,
    )


if __name__ == "__main__":
    main()
