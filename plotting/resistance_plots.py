import os
import json
import matplotlib.pyplot as plt
import numpy as np

def process_json_file(filename, histograms):
    with open(filename, 'r') as file:
        data = json.load(file)
        wagon_chip_data = data["data"]["wagon type chip"]
#        print(wagon_chip_data)
        for key, value in wagon_chip_data.items():
#            print(key, value)
            if isinstance(value[0], float):
#                if value[0] > 64.5:
                print(filename, key, value[0])
                histograms[key].append(value[0])

def main():
    histograms = {
        "VMON_REF0 -> PROBE_DC": [],
        "X_RESETb -> PWR_EN": [],
        "WAGON_TYPE -> VMON_REF1": [],
        "VMON_REF2 -> PROBE_DC": []
    }

    # Mapping dictionary for display names
    display_names = {
        "VMON_REF0 -> PROBE_DC": "VMON_REF0_to_PROBE_DC",
        "X_RESETb -> PWR_EN": "PWR_EN_to_X_RESETb",
        "WAGON_TYPE -> VMON_REF1": "VMON_REF1_to_WAGON_TYPE",
        "VMON_REF2 -> PROBE_DC": "VMON_REF2_to_PROBE_DC"
    }

    # List all JSON files and sort them based on file number
    json_files = [filename for filename in os.listdir('./jsons/IDResistanceTest') if filename.endswith('.json') and filename.startswith('IDResistanceTest_')]

    # Filter out filenames with invalid file numbers
    valid_files = []
    for filename in json_files:
        try:
            file_number = int(filename[-8:-5].lstrip('0'))
            if 1 <= file_number <= 124:
                valid_files.append((filename, file_number))
        except ValueError:
            pass
    #json_files.sort(key=lambda x: int(x[-8:-5].lstrip('0')))

# Sort the list of valid JSON files based on file number
    valid_files.sort(key=lambda x: x[1])

    # Process JSON files in sorted order
    for filename, _ in valid_files:
        print(filename)

    for filename, _ in valid_files:
        print(filename)
        if filename.endswith('.json') and filename.startswith('IDResistanceTest_'):
            file_number = filename[-8:-5].lstrip('0')
            if file_number.isdigit() and 1 <= int(file_number) <= 124:
                process_json_file('./jsons/IDResistanceTest/'+filename, histograms)

    # Plotting individual histograms for each resistance
    for key, values in histograms.items():
        display_name = display_names[key]
        plt.figure(figsize=(8, 6))
        plt.hist(values, bins=20, alpha=0.5, label=display_name)
        plt.xlabel('Resistance')
        plt.ylabel('Counts')
        plt.title(f'{display_name} Resistance')
        plt.legend(loc='upper right')

        # Calculate and annotate number of events, mean, and standard deviation
        num_events = len(values)
        mean = np.mean(values)
        std_dev = np.std(values)
        annotation_text = f'Num Events: {num_events}\nMean: {mean:.2f}\nStd Dev: {std_dev:.2f}'
        plt.text(0.785, 0.8, annotation_text, fontsize=10, transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.2))

        # Save the plot as a PDF
        plt.savefig(f'{display_name}_Resistance.pdf', bbox_inches='tight')

        plt.close()
#        plt.show()

if __name__ == "__main__":
    main()
