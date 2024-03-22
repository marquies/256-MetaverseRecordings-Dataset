# import sys
import os
import csv
import cv2
import ffmpeg
import random
import shutil


# Function to convert timestamp in 'HH:MM:SS' format to seconds
def timestamp_mmssms_to_frame(timestamp, framerate):
    mm, ss, ms = map(int, timestamp.split(':'))
    frame = (mm * 60 + ss) * framerate
    framePer10ms = float(framerate) / float(100)
    frame += ms * framePer10ms
    frame = int(frame)
    return frame


# Function to convert source videos to 720p 30fps
def convert_video720p(videoRaw_dir, video720p_dir):
    entries = os.listdir(videoRaw_dir)
    mp4_files = [entry
                 for entry in entries
                 if os.path.splitext(entry)[1].lower() == '.mp4']
    for file in mp4_files:
        print(f"Converting now {videoRaw_dir + file}.")
        print(f"Output is written to {video720p_dir + file}.")
        (
            ffmpeg
            .input(videoRaw_dir + file)
            .filter('scale', 1280, 720)
            .filter('fps', fps=30)
            .output(video720p_dir + file, vcodec='libx264',
                    acodec='aac', audio_bitrate='192k')
            .run()
        )
    print("Finished converting video.")


# Exporting images based on the timestamps
def export_images(stampsFile, video_dir, images_dir):
    with open(stampsFile, newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Skip header row
        next(csv_reader)
        # Iterate over each annotation and save frame from video
        for filename, stamp in csv_reader:
            cap = cv2.VideoCapture(video_dir + filename)
            frame = timestamp_mmssms_to_frame(stamp, 30)

            # Set video position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame)

            # Read the frame and save it as .png
            success, frame = cap.read()
            if success:
                cv2.imwrite("".join([images_dir,
                                     os.path.splitext(filename)[0],
                                     "_",
                                     stamp.replace(':', '_'),
                                     ".png"]),
                            frame)
            else:
                print(f"Failed to capture frame at {stamp}.")
            cap.release()
    print("Finished extraction of images.")


def train_test_val_split(images_dir, imagesAvatar_dir,
                         train_dir, val_dir, test_dir,
                         train_size=0.7, test_val_size=0.15):
    # Get all file names
    images_files = os.listdir(images_dir)
    random.shuffle(images_files)  # Shuffle the files
    # Calculate split sizes
    train_count = int(len(images_files) * train_size)
    test_val_count = int(len(images_files) * test_val_size)
    # Split file names
    train_files = images_files[:train_count]
    val_files = images_files[train_count:train_count + test_val_count]
    test_files = images_files[train_count + test_val_count:]

    # Copy files to the respective directories
    for file in train_files:
        file, _ = file.split(".png")
        shutil.copy(os.path.join(images_dir, (file + ".png")),
                    os.path.join(train_dir, "images", (file + ".png")))
        shutil.copy(os.path.join(imagesAvatar_dir, (file + ".txt")),
                    os.path.join(train_dir, "labels", (file + ".txt")))

    for file in val_files:
        file, _ = file.split(".png")
        shutil.copy(os.path.join(images_dir, (file + ".png")),
                    os.path.join(val_dir, "images", (file + ".png")))
        shutil.copy(os.path.join(imagesAvatar_dir, (file + ".txt")),
                    os.path.join(val_dir, "labels", (file + ".txt")))

    for file in test_files:
        file, _ = file.split(".png")
        shutil.copy(os.path.join(images_dir, (file + ".png")),
                    os.path.join(test_dir, "images", (file + ".png")))
        shutil.copy(os.path.join(imagesAvatar_dir, (file + ".txt")),
                    os.path.join(test_dir, "labels", (file + ".txt")))
    print("Finished splitting data to yolov7.")


def main(video_flag=False, images_flag=False, split_flag=False):
    # Video input path
    videoRaw_dir = os.getcwd() + "/metaverse-dataset/output-videos/"
    # Video output path
    video720p_dir = os.getcwd() + "/TrainTestData/Videos720p/"
    # Timestamps of the avatar frames
    timestampsCsvFile = os.getcwd() + "/TimestampsForExport.csv"
    # Image output path
    images_dir = os.getcwd() + "/TrainTestData/ImagesRaw/"
    # Annotations path manually created
    imagesAvatar_dir = os.getcwd() + "/TrainTestData/ImagesAvatar/"
    # Train dir
    train_dir = os.getcwd() + "/yolov7/train"
    # Val dir
    val_dir = os.getcwd() + "/yolov7/val"
    # Test dir
    test_dir = os.getcwd() + "/yolov7/test"

    if video_flag:
        convert_video720p(videoRaw_dir, video720p_dir)

    if images_flag:
        export_images(timestampsCsvFile, video720p_dir, images_dir)

    if split_flag:
        train_test_val_split(images_dir, imagesAvatar_dir, train_dir, val_dir,
                             test_dir)


if __name__ == "__main__":
    video_flag = False
    images_flag = False
    split_flag = False
    # if sys.argv[1] == "video" or sys.argv[1] == "Video":
    #     video_flag = True
    #
    # if sys.argv[2] == "images" or sys.argv[2] == "Images":
    #     images_flag = True

    main(video_flag, images_flag, split_flag)
