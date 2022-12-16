import argparse 

parser = argparse.ArgumentParser(description='Anonymize DICOM files by overwriting potentially identifying information.')
parser.add_argument('dcm', help='Path to the DICOM directory')
parser.add_argument('out', help='Path to the output folder, where the anonymized DICOM files will be stored')
parser.add_argument('-ext', '--ext', help='Extension of the DICOM files. Default is .IMA', default='.IMA')
parser.add_argument('-t', '--tags', help='DICOM tags to be anonymized. Default is PatientID, PatientName, and PatientBirthDate. Add more here if you want to overwrite more.', nargs='+', default=None)
parser.add_argument('-m', '--mapping', help='Path to the mapping file. Default is None', default=None)
parser.add_argument('-id', '--id', help='Participant ID to be used', default=None)
parser.add_argument('-name', '--name', help='Participant name to be used - must be dirname in dcm folder', default=None)
parser.add_argument('-d', '--dcm_dirs_as_ids', help='Use the DICOM directory names as the participant IDs. Default is False', action='store_true', default=False)
p = parser.parse_args()

class dcmanon:
    
    def __init__(self, dcm, out, ext, tags=None, mapping=None, name=None, id=None, dcm_dirs_as_ids=False):

        from os.path import join, exists
        from os import listdir as ls
        from tqdm import tqdm
        
        self.dcm = dcm
        self.out = out
        self.ext = ext
        self.tags = tags
        self.mapping = mapping
        self.name = name
        self.id = id
        self.subjects = None
        self.dcm_dirs_as_ids = dcm_dirs_as_ids

        # DICOM elements to be anonymized - overwritten with ''
        self.elements = ['PatientName','PatientBirthDate']

        # Add elements to be anonymized if provided
        if self.tags is not None:
            self.elements += self.tags

        # Check if the input folder exists
        if not exists(self.dcm):
            raise Exception(f'Folder {self.dcm} does not exist')

        # Check if the output folder exists
        if not exists(self.out):
            raise Exception(f'Folder {self.out} does not exist')

        # If the mapping file is provided, read it
        if self.mapping is not None:
            #TODO
            pass

        if self.dcm_dirs_as_ids:
            # Get the list of subject folders
            self.subjects = [f for f in ls(self.dcm) if exists(join(self.dcm, f))]
            print(f'Found {len(self.subjects)} subjects in {self.dcm}')

            print('Anonymising DICOM files...')
            print(f'Anonymised data will be save in the {self.out}')

            # Set progress bar
            pbar = tqdm(self.subjects)

            for s in pbar:
                pbar.set_description(f'Anonymising sub-{s}')
                self.name = s
                self.id = s
                self.process()

    def loadmapping(self):
        # Load mapping file
        import pandas as pd
        pass

    def process(self):
        # Process subject

        from pydicom import dcmread
        from os.path import join, exists
        from os import walk, mkdir
        from os import listdir as ls

        # Check if the subject folder exists
        if not exists(join(self.dcm, self.name)):
            raise Exception(f'Folder {self.name} does not exist')

        # create folder for the anonymized data
        if not exists(self.out):
            mkdir(self.out)

        # create folder for the subject
        if not exists(join(self.out, self.id)):
            mkdir(join(self.out, self.id))

        for root, dirs, __ in walk(join(self.dcm, self.name)):

            for d in dirs:

                files = [f for f in ls(join(root, d)) if f.endswith(self.ext)]
                
                # Only process folders with any DICOM files of specified extension
                if len(files) > 0:
                    
                    # If we have DICOM files, create a folder for the session in out folder
                    if not exists(join(self.out, self.id, d)):
                        mkdir(join(self.out, self.id, d))
                    
                    # Loop through the files and anonymize them
                    for f in files:
                        
                        f_in_path = join(root, d, f)
                        
                        # Load the data to memory
                        ds = dcmread(f_in_path)
                        
                        # anonymize the data
                        for b in self.elements:
                            ds.data_element(b).value = ''
                        
                        # Replace the subject ID
                        ds.data_element('PatientID').value = self.id

                        # need to replace the subs name in the file name
                        fname = f.replace(f.split('.')[0], str(self.id))
                        
                        # save the file
                        ds.save_as(join(self.out, self.id, d, fname))


