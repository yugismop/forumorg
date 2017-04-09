import json

from deepdiff import DeepDiff


def get_diff(old_company, company):
    try:
        diff = DeepDiff(old_company, company, ignore_order=True, verbose_level=2).json
    except Exception as e:
        diff = {'error': e}

    try:
        root = json.loads(diff)
        if root.get('dictionary_item_added'):
            root = root.get('dictionary_item_added')
            if 'furnitures' in root.keys()[0]:
                equipement = root.values()[0]
                furniture = root.keys()[0].split('[')[3].replace(']', '').replace('\'', '')
                diff = 'Passage de 0 à {} unités pour {}'.format(equipement, furniture)
            if 'catering' in root.keys()[0]:
                repas = root.values()[0]
                day = 'Mercredi' if 'wed' in root.keys()[0] else 'Jeudi'
                diff = 'Passage de 0 à {} repas pour le {}'.format(repas, day)

        if root.get('iterable_item_added'):
            root = root.get('iterable_item_added')
            if 'persons' in root.keys()[0]:
                badge = root.values()[0]
                diff = 'Ajout de {}    {}    {}'.format(badge.get('name'), badge.get('function'), badge.get('days'))
            if 'transports' in root.keys()[0]:
                transport = root.values()[0]
                diff = 'De {} vers {} à {} ({}, Nb: {})'.format(transport.get('departure_place'),
                                                                transport.get('arrival_place'), transport.get('departure_time'), transport.get('phone'), transport.get('nb_persons'))
                if transport.get('comment'):
                    diff += ' Commentaire: {}'.format(transport.get('comment'))

        if root.get('values_changed'):
            root = root.get('values_changed')
            if 'catering' in root.keys()[0]:
                repas = root.values()[0]
                day = 'Mercredi' if 'wed' in root.keys()[0] else 'Jeudi'
                diff = 'Passage de {} à {} repas pour le {}'.format(repas.get('old_value'), repas.get('new_value'), day)
            if 'furnitures' in root.keys()[0]:
                equipement = root.values()[0]
                furniture = root.keys()[0].split('[')[3].replace(']', '').replace('\'', '')
                diff = 'Passage de {} à {} unités pour {}'.format(equipement.get('old_value'), equipement.get('new_value'), furniture)
    except Exception as e:
        print('JSON parsing has failed')  # do nothing if translation fails
