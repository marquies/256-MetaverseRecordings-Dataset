from glob import glob
import csv

print("New run.")
fnames = glob("labels/*")

for file in fnames:
    print(file)
    with open(file, 'r', newline='') as csvr:
        with open("labelsMod/" + file[7:], 'w') as csvw:
            reader = csv.reader(csvr, delimiter=' ')
            writer = csv.writer(csvw, delimiter=' ')
            for row in reader:
                row[0] = "0"
                print("New row.")
                print(row)
                writer.writerow(row)
