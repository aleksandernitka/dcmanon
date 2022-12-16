import argparse 
from pydicom import dcmread
from os.path import join, exists
from os import walk, mkdir
from os import listdir as ls
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Anonymize DICOM files by overwriting potentially identifying information. ')
parser.add_argument('dcm', help='Path to the DICOM dir - effectively it is the name of the folder with DICOM files')
parser.add_argument('id', help='Participant ID to be used')
parser.add_argument('out', help='Path to the output folder, where the anonymized DICOM files will be stored')
parser.add_argument('-ext', '--ext', help='Extension of the DICOM files. Default is .IMA', default='.IMA')
p = parser.parse_args()

# DICOM elements to be anonymized - overwritten with ''
elements = ['PatientName','PatientBirthDate']

# TODO - check if the folder with DICOM files exists

# create folder for the anonymized data
if not exists(p.out):
    mkdir(p.out)

# create folder for the subject
if not exists(join(p.out, p.id)):
    mkdir(join(p.out, p.id))

for root, dirs, __ in walk(p.dcm):

    for d in dirs:

        files = [f for f in ls(join(root, d)) if f.endswith(p.ext)]
        # print(f'sub-{sub}: {d} has {len(files)} {ext} file(s)')
        if len(files) > 0:
            
            # If we have DICOM files, create a folder for the session in out folder
            if not exists(join(p.out, p.id, d)):
                mkdir(join(p.out, p.id, d))
            
            # Loop through the files and anonymize them
            pbar = tqdm(files)
            for f in pbar:
                pbar.set_description(f'Anonymising sub-{p.id} {d}')
                f_in_path = join(root, d, f)
                
                # Load the data to memory
                ds = dcmread(f_in_path)
                
                # anonymize the data
                for b in elements:
                    ds.data_element(b).value = ''
                
                # Replace the subject ID
                ds.data_element('PatientID').value = p.id

                # need to replace the subs name in the file name
                fname = f.replace(str(p.dcm).split('/')[-1], str(p.id))
                
                # save the file
                ds.save_as(join(p.out, p.id, d, fname))


