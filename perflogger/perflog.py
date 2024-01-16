'''
The Performance Logging Module
'''
import os
import datetime
import json
import yaml
from helpers.file import write_file, create_dir_struct


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

        # if 'hierarchical' in self.config and self.config['hierarchical']:
        #     self._save_config_hierarchical()
        # else:
        #     self._save_config_single()

    def add_perflog(self, client_id: str, round_num: int, metrics: dict, time_delta: float) -> None:
        '''
        Add a Performance Log Row to the perflogs
        '''
        if len(self.perflogs) == 0:
            self._generate_csv_header(metrics)

        self.perflogs.append(self._metrics_to_csvline(
            client_id, round_num, metrics, time_delta))

    def save(self):
        '''
        Save the Performance Log
        '''

        self._save_perflog()

    def save_params(self, round_num: int, params: dict):
        '''
        Save the Global Model Parameters
        '''
        write_file(f'{round_num}.json', f'{self.project_path}/params',
                   json.dumps(params, indent=4))

    def _metrics_to_csvline(self, client_id: str, round_num: int, metrics: dict, time_delta: float) -> str:
        '''
        Generate a CSV string row from a dictionary of metrics
        '''
        record = f'{client_id},{round_num},'
        for key in self.metric_names:
            if key in ['confusion_matrix', 'classification_report']:
                continue
            record += f'{metrics[key]:.6f},'

        self._save_extra_metrics(client_id, round_num, metrics)

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
        self.csv_header = 'node,round,'
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

    def _save_config_single(self) -> None:

        # write client_params.dataset.preprocessor
        write_file('preprocessor.py', f'{self.project_path}/modules',
                   self.config['client_params']['dataset']['preprocessor']['content'])
        self.config['client_params']['dataset']['preprocessor'] = \
            self.config['client_params']['dataset']['preprocessor']['file']

        # write client_params.dataset.distribution.distributor
        write_file('distributor.py', f'{self.project_path}/modules',
                   self.config['client_params']['dataset']['distribution']['distributor']['content'])
        self.config['client_params']['dataset']['distribution']['distributor'] = \
            self.config['client_params']['dataset']['distribution']['distributor']['file']

        # write model_params.model_file
        write_file('model_file.py', f'{self.project_path}/modules',
                   self.config['client_params']['model_params']['model_file']['content'])
        self.config['client_params']['model_params']['model_file'] = \
            self.config['client_params']['model_params']['model_file']['file']

        # write model_params.parameter_mixer
        write_file('parameter_mixer.py', f'{self.project_path}/modules',
                   self.config['client_params']['model_params']['parameter_mixer']['content'])
        self.config['client_params']['model_params']['parameter_mixer'] = \
            self.config['client_params']['model_params']['parameter_mixer']['file']

        # write model_params.training_loop_file
        write_file('training_loop_file.py', f'{self.project_path}/modules',
                   self.config['client_params']['model_params']['training_loop_file']['content'])
        self.config['client_params']['model_params']['training_loop_file'] = \
            self.config['client_params']['model_params']['training_loop_file']['file']

        # write model_params.test_file
        write_file('test_file.py', f'{self.project_path}/modules',
                   self.config['client_params']['model_params']['test_file']['content'])
        self.config['client_params']['model_params']['test_file'] = \
            self.config['client_params']['model_params']['test_file']['file']

        # write server_params.aggregator
        write_file('aggregator.py', f'{self.project_path}/modules',
                   self.config['server_params']['aggregator']['content'])
        self.config['server_params']['aggregator'] = \
            self.config['server_params']['aggregator']['file']

        # write server_params.model_file
        write_file('server.model_file.py', f'{self.project_path}/modules',
                   self.config['server_params']['model_file']['content'])
        self.config['server_params']['model_file'] = \
            self.config['server_params']['model_file']['file']

        # write server_params.test_file
        write_file('server.test_file.py', f'{self.project_path}/modules',
                   self.config['server_params']['test_file']['content'])
        self.config['server_params']['test_file'] = \
            self.config['server_params']['test_file']['file']

        # write dataset_params.prep
        write_file('dataset_prep.py', f'{self.project_path}/modules',
                   self.config['dataset_params']['prep']['content'])
        self.config['dataset_params']['prep'] = \
            self.config['dataset_params']['prep']['file']

        # write the final config file
        config = {
            'project_name': self.config['project_name'],
            'dataset_params': self.config['dataset_params'],
            'client_params': self.config['client_params'],
            'server_params': self.config['server_params']
        }

        write_file('config.yaml', f'{self.project_path}',
                   yaml.dump(config, default_flow_style=False))

        # write the initial global parameters
        write_file('0.json', f'{self.project_path}/params',
                   json.dumps(self.config['exec_params']['central_model_param'], indent=4))

    def _save_config_hierarchical(self) -> None:

        # write client_params.dataset.distribution.distributor
        write_file('distributor.py', f'{self.project_path}/modules',
                   self.config['client_params']['dataset']['distribution']['distributor']['content'])
        self.config['client_params']['dataset']['distribution']['distributor'] = \
            self.config['client_params']['dataset']['distribution']['distributor']['file']

        # recursively load middleware_params modules
        self._recursive_config_dumper(
            self.config['client_params'], f'{self.project_path}/modules')

        # write server_params.aggregator
        write_file('aggregator.py', f'{self.project_path}/modules',
                   self.config['server_params']['aggregator']['content'])
        self.config['server_params']['aggregator'] = \
            self.config['server_params']['aggregator']['file']

        # write server_params.model_file
        write_file('model_file.py', f'{self.project_path}/modules',
                   self.config['server_params']['model_file']['content'])
        self.config['server_params']['model_file'] = \
            self.config['server_params']['model_file']['file']

        # write server_params.test_file
        write_file('test_file.py', f'{self.project_path}/modules',
                   self.config['server_params']['test_file']['content'])
        self.config['server_params']['test_file'] = \
            self.config['server_params']['test_file']['file']

        # write dataset_params.prep
        write_file('dataset_prep.py', f'{self.project_path}/modules',
                   self.config['dataset_params']['prep']['content'])
        self.config['dataset_params']['prep'] = \
            self.config['dataset_params']['prep']['file']

        # write the final config file
        config = {
            'project_name': self.config['project_name'],
            'dataset_params': self.config['dataset_params'],
            'client_params': self.config['client_params'],
            'server_params': self.config['server_params']
        }

        write_file('config.yaml', f'{self.project_path}',
                   yaml.dump(config, default_flow_style=False))

        # write the initial global parameters
        write_file('0.json', f'{self.project_path}/params',
                   json.dumps(self.config['exec_params']['central_model_param'], indent=4))

    def _recursive_config_dumper(self, middleware_params: dict, dir: str):
        '''
        Recursively Load the hierarchical structure configs for the middlewares
        '''

        for i, middleware in enumerate(middleware_params['individual_configs']):
            middleware_dir = os.path.join(dir, f'mw{i}')
            create_dir_struct(middleware_dir)

            if 'individual_configs' in middleware:
                self._recursive_config_dumper(middleware, middleware_dir)

            # write client_params.aggregation.aggregator
            write_file('aggregator.py', middleware_dir,
                       middleware['aggregation']['aggregator']['content'])
            middleware['aggregation']['aggregator'] = \
                middleware['aggregation']['aggregator']['file']

            # write client_params.dataset.preprocessor
            write_file('preprocessor.py', middleware_dir,
                       middleware['dataset']['preprocessor']['content'])
            middleware['dataset']['preprocessor'] = \
                middleware['dataset']['preprocessor']['file']

            # write client_params.dataset.distribution.distributor
            write_file('distributor.py', middleware_dir,
                       middleware['dataset']['distribution']['distributor']['content'])
            middleware['dataset']['distribution']['distributor'] = \
                middleware['dataset']['distribution']['distributor']['file']

            # write  model_params.model_file
            write_file('model_file.py', middleware_dir,
                       middleware['model_params']['model_file']['content'])
            middleware['model_params']['model_file'] = \
                middleware['model_params']['model_file']['file']

            # write   model_params.parameter_mixer
            write_file('parameter_mixer.py', middleware_dir,
                       middleware['model_params']['parameter_mixer']['content'])
            middleware['model_params']['parameter_mixer'] = \
                middleware['model_params']['parameter_mixer']['file']

            # write model_params.training_loop_file
            write_file('training_loop_file.py', middleware_dir,
                       middleware['model_params']['training_loop_file']['content'])
            middleware['model_params']['training_loop_file'] = \
                middleware['model_params']['training_loop_file']['file']

            # write model_params.test_file
            write_file('test_file.py', middleware_dir,
                       middleware['model_params']['test_file']['content'])
            middleware['model_params']['test_file'] = \
                middleware['model_params']['test_file']['file']

            middleware_params['individual_configs'][i] = middleware

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
