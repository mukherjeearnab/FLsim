'''
Module defining the job object for dataset management
'''


class Job(object):
    '''
    JOb Information Class for Dataset Management
    '''

    def __init__(self, job_name: str, manifest: dict):
        '''
        constructor
        '''
        self.job_name = job_name
        self.manifest = manifest
        self.dataset_prep_mod = None
        self.dataset_root_path = None
        self.cluster2chunk_mapping = dict()
