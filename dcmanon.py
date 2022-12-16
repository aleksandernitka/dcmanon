import argparse 

parser = argparse.ArgumentParser(description='Anonymize DICOM files by overwriting potentially identifying information. ')
parser.add_argument('dcm', help='Path to the DICOM dir - effectively it is the name of the folder with DICOM files')
parser.add_argument('id', help='Participant ID to be used')
parser.add_argument('out', help='Path to the output folder, where the anonymized DICOM files will be stored')
parser.add_argument('-ext', '--ext', help='Extension of the DICOM files. Default is .IMA', default='.IMA')
parser.add_argument('-t', '--tags', help='DICOM tags to be anonymized. Default is PatientID, PatientName, and PatientBirthDate. Add more here if you want to overwrite more.', nargs='+', default=None)
p = parser.parse_args()

class dcmanon:
    
    def __init__(self, dcm, id, out, ext, tags):

        from pydicom import dcmread
        from os.path import join, exists
        from os import walk, mkdir
        from os import listdir as ls
        from tqdm import tqdm
        
        self.dcm = dcm
        self.id = id
        self.out = out
        self.ext = ext
        self.tags = tags

        # DICOM elements to be anonymized - overwritten with ''
        self.elements = ['PatientName','PatientBirthDate']

        if self.tags is not None:
            self.elements += self.tags

        if not exists(self.dcm):
            raise Exception(f'Folder {self.dcm} does not exist')

        # create folder for the anonymized data
        if not exists(self.out):
            mkdir(self.out)

        # create folder for the subject
        if not exists(join(self.out, self.id)):
            mkdir(join(self.out, self.id))

        for root, dirs, __ in walk(self.dcm):

            for d in dirs:

                files = [f for f in ls(join(root, d)) if f.endswith(self.ext)]
                # print(f'sub-{sub}: {d} has {len(files)} {ext} file(s)')
                if len(files) > 0:
                    
                    # If we have DICOM files, create a folder for the session in out folder
                    if not exists(join(self.out, self.id, d)):
                        mkdir(join(self.out, self.id, d))
                    
                    # Loop through the files and anonymize them
                    pbar = tqdm(files)
                    for f in pbar:
                        pbar.set_description(f'Anonymising sub-{self.id} {d}')
                        f_in_path = join(root, d, f)
                        
                        # Load the data to memory
                        ds = dcmread(f_in_path)
                        
                        # anonymize the data
                        for b in elements:
                            ds.data_element(b).value = ''
                        
                        # Replace the subject ID
                        ds.data_element('PatientID').value = self.id

                        # need to replace the subs name in the file name
                        fname = f.replace(str(self.dcm).split('/')[-1], str(self.id))
                        
                        # save the file
                        ds.save_as(join(self.out, self.id, d, fname))


