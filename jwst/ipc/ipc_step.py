from jwst.stpipe import Step
from jwst import datamodels
from . import ipc_corr


class IPCStep(Step):
    """
    IPCStep: Performs IPC correction by convolving the input science
    data model with the IPC reference data.
    """

    reference_file_types = ['ipc']

    def process(self, input):

        # Open the input data model
        with models.open(input) as input_model:

            # Get the name of the ipc reference file to use
            self.ipc_name = self.get_reference_file(input_model, 'ipc')
            self.log.info('Using IPC reference file %s', self.ipc_name)

            # Check for a valid reference file
            if self.ipc_name == 'N/A':
                self.log.warning('No IPC reference file found')
                self.log.warning('IPC step will be skipped')
                result = input_model.copy()
                result.meta.cal_step.ipc = 'SKIPPED'
                return result

            # Open the ipc reference file data model
            ipc_model = models.IPCModel(self.ipc_name)

            # Do the ipc correction
            result = ipc_corr.do_correction(input_model, ipc_model)

            # Close the reference file and update the step status
            ipc_model.close()
            result.meta.cal_step.ipc = 'COMPLETE'

        return result
