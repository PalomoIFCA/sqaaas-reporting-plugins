import logging
import re

from report2sqaaas import utils as sqaaas_utils


logger = logging.getLogger('sqaaas.reporting.plugins.json_not_empty')


class JsonNotEmptyValidator(sqaaas_utils.BaseValidator):
    valid = False
    standard = {
        'title': (
            'A set of Common Software Quality Assurance Baseline Criteria for '
            'Research Projects'
        ),
        'version': 'v4.0',
        'url': 'https://github.com/indigo-dc/sqa-baseline/releases/tag/v4.0',
    }

    def get_criterion(self):
        criterion = None
        pattern = '(^(SvcQC|QC)\.[A-Z][a-z]{2})'
        match = re.search(pattern, self.opts.subcriterion)
        if match:
            criterion = match.group(0)
            logger.debug('Matching criterion found: %s' % criterion)
        return criterion

    def validate(self):
        criterion = self.get_criterion()
        criterion_data = sqaaas_utils.load_criterion_from_standard(
            criterion
        )
        subcriteria = []
        subcriterion_data = criterion_data[self.opts.subcriterion]
        subcriterion_valid = False
        evidence = None

        try:
            data = sqaaas_utils.load_json(self.opts.stdout)
        except ValueError as e:
            data = {}
            logger.error('Input data does not contain a valid JSON: %s' % e)
        else:
            if data:
                evidence = subcriterion_data['evidence']['success']
                logger.debug('Found a non-empty JSON payload')
            else:
                evidence = subcriterion_data['evidence']['failure']
                logger.debug('JSON payload is empty')

        if evidence:
            logger.info(evidence)

        self.valid = subcriterion_valid
        requirement_level = subcriterion_data['requirement_level']
        if (
            (not subcriterion_valid) and
            (requirement_level in ['MUST'])
        ):
            self.valid = False

        subcriteria.append({
            'id': self.opts.subcriterion,
            'description': subcriterion_data['description'],
            'valid': subcriterion_valid,
            'evidence': evidence,
            'standard': self.standard
        })

        return {
            'valid': self.valid,
            'subcriteria': subcriteria,
            'data_unstructured': data
        }
