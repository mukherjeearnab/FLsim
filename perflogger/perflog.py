'''
The Performance Logging Module
'''
import threading
import datetime
import json
from helpers.file import write_file
from helpers.sysmon import monitor_process


class PerformanceLog(object):
    '''
    Performance Logging Class
    '''

    def __init__(self, project_name: str, config: str) -> None:
        self.project_name = project_name
        self.perflogs = []
        self.config = config

        self.metric_names = None
        self.csv_header = None

        self.project_time = '{date:%Y-%m-%d_%H:%M:%S}'.format(
            date=datetime.datetime.now())
        self.project_path = f"./projects/{self.project_name}-{self.project_time}/"

        self._save_config()
        self.start_resource_logger()

    def start_resource_logger(self):
        '''
        Start the resource logger for system
        '''

        resource_file_name = f'{self.project_path}resource.csv'

        t1 = threading.Thread(target=monitor_process, args=(
            resource_file_name,), daemon=True)

        t1.start()

    def add_perflog(self, cluster_id: str, node_id: str, node_type: str, round_num: str, epoch_num: str, metrics: dict, time_delta: float) -> None:
        '''
        Add a Performance Log Row to the perflogs
        '''
        if len(self.perflogs) == 0:
            self._generate_csv_header(metrics)

        self.perflogs.append(self._metrics_to_csvline(
            cluster_id, node_id, node_type, round_num, epoch_num, metrics, time_delta))

    def save(self):
        '''
        Save the Performance Log
        '''

        self._save_perflog()

    def save_params(self, round_num: int, params: dict):
        '''
        Save the Global Model Parameters
        '''
        write_file(f'{round_num}.txt', f'{self.project_path}/params',
                   params)

    def _metrics_to_csvline(self, cluster_id: str, node_id: str, node_type: str, round_num: str, epoch_num: str, metrics: dict, time_delta: float) -> str:
        '''
        Generate a CSV string row from a dictionary of metrics
        '''
        record = f'{cluster_id},{node_id},{node_type},{round_num},{epoch_num},'
        for key in self.metric_names:
            if key in ['confusion_matrix', 'classification_report']:
                continue
            record += f'{metrics[key]:.6f},'

        self._save_extra_metrics(
            f'{cluster_id}-{node_id}-{node_type}', round_num, metrics)

        # finally add time_delta
        record += f'{time_delta},'

        record = record[:-1] + '\n'
        return record

    def _save_extra_metrics(self, client_id: str, round_num: int, metrics: dict) -> None:
        '''
        Save Extra Metrics such as confusion matrics and classification reports
        '''

        # save confusion matrix
        write_file(f'{client_id}.txt', f'{self.project_path}/extra-metrics/confusion-matrix',
                   f"Round {round_num}: \n{self._confusion_matrix_to_str(metrics['confusion_matrix'])}\n", 'a')

        # save classification report
        write_file(f'{client_id}.txt', f'{self.project_path}/extra-metrics/classification-report',
                   f"Round {round_num}: \n{metrics['classification_report']}\n", 'a')

    def _generate_csv_header(self, metrics: dict) -> None:
        '''
        Generate the CSV header from the metrics dictionary
        '''
        self.csv_header = 'cluster_id,node_id,node_type,global_round,cluster_epoch,'
        self.metric_names = list(metrics.keys())
        for key in self.metric_names:
            if key in ['confusion_matrix', 'classification_report']:
                continue
            self.csv_header += f'{key},'

        # add time_delta header
        self.csv_header += 'time_delta,'
        self.csv_header = self.csv_header[:-1] + '\n'

    def _save_perflog(self) -> None:
        '''
        Save the Perflog as a CSV file
        '''

        csv_string = self.csv_header
        for line in self.perflogs:
            csv_string += line

        write_file('perflog.csv', self.project_path,
                   csv_string)

    def _save_config(self) -> None:
        '''
        Save the configuration and execution states of the job
        '''

        # save the job config yaml file
        write_file('config.yaml', f'{self.project_path}/config',
                   self.config['raw_config'])

        # save the dataset metadata from the dataset distribution
        content = json.dumps(self.config['dist_metadata'], indent=4)
        write_file('distribution_metadata.json', f'{self.project_path}/config',
                   content)

        # save the dataset metadata from controller
        content = json.dumps(self.config['dataset_manifest'], indent=4)
        write_file('dataset_manifest.json', f'{self.project_path}/config',
                   content)

        # save the templates of the job
        for template in self.config['config']['templates']:
            filename = template['path'].split('/')[-1]
            directory = template['path'].replace(filename, '')
            directory = directory.replace('./', '')

            path = f'{self.project_path}/config/{directory}'

            write_file(filename, path, template['content'])

    def _confusion_matrix_to_str(self, matrix: list) -> str:
        '''
        Get A Pretty Printed Version of the Confusion Matrix
        '''

        mat_str = ''

        for _, row in enumerate(matrix):
            mat_str += '[ '
            for _, col in enumerate(row):
                mat_str += f'{col},\t\t'

            mat_str += ']\n'

        return mat_str
