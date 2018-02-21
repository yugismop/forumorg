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
            keys = list(root.keys())[0]
            values = list(root.values())[0]

            if 'furnitures' in keys:
                equipement = values
                furniture = keys.split('[')[3].replace(']', '').replace('\'', '')
                diff = 'Passage de 0 à {} unités pour {}'.format(equipement, furniture)

            if 'catering' in keys:
                repas = values
                day = 'Mercredi' if 'wed' in keys else 'Jeudi'
                diff = 'Passage de 0 à {} repas pour le {}'.format(repas, day)

            if 'events' in keys:
                event = keys.split('[')[3].replace(']', '').replace('\'', '')
                diff = 'Inscription de {}'.format(event)

        if root.get('iterable_item_added'):
            root = root.get('iterable_item_added')
            keys = list(root.keys())[0]
            values = list(root.values())[0]

            if 'persons' in keys:
                badge = values
                diff = 'Ajout de {}    {}    {}'.format(badge.get('name'), badge.get('function'), badge.get('days'))
            if 'transports' in keys:
                transport = values
                diff = 'De {} vers {} à {} ({}, Nb: {})'.format(transport.get('departure_place'),
                                                    transport.get('arrival_place'), transport.get('departure_time'), 
                                                    transport.get('phone'), transport.get('nb_persons'))
                if transport.get('comment'):
                    diff += ' Commentaire: {}'.format(transport.get('comment'))

        if root.get('values_changed'):
            root = root.get('values_changed')
            keys = list(root.keys())[0]
            values = list(root.values())[0]

            if 'catering' in keys:
                repas = values
                day = 'Mercredi' if 'wed' in keys else 'Jeudi'
                diff = 'Passage de {} à {} repas pour le {}'.format(repas.get('old_value'), 
                                                                repas.get('new_value'), day)

            if 'furnitures' in keys:
                equipement = values
                furniture = keys.split('[')[3].replace(']', '').replace('\'', '')
                diff = 'Passage de {} à {} unités pour {}'.format(equipement.get('old_value'),
                                                      equipement.get('new_value'), furniture)
            
            if 'events' in keys:
                etat = values
                event = keys.split('[')[3].replace(']', '').replace('\'', '')
                if etat.get('new_value'):
                    diff = 'Inscription de {}'.format(event)
                else:
                    diff = 'Désinscription de {}'.format(event)

        if root.get('dictionary_item_removed'):
                root = root.get('dictionary_item_removed')
                keys = list(root.keys())[0]
                values = list(root.values())[0]

                if 'catering' in keys:
                    repas = values
                    day = 'Mercredi' if 'wed' in keys else 'Jeudi'
                    diff = 'Passage de {} à 0 repas pour le {}'.format(repas, day)

                if 'furnitures' in keys:
                    equipement = values
                    furniture = keys.split('[')[3].replace(']', '').replace('\'', '')
                    diff = 'Passage de {} à 0 unités pour {}'.format(equipement, furniture)

        if root.get('iterable_item_removed'):
            root = root.get('iterable_item_removed')
            keys = list(root.keys())[0]
            values = list(root.values())[0]      
            if 'persons' in keys:
                badge = values
                diff = 'Supression de {}    {}    {}'.format(badge.get('name'), 
                                                        badge.get('function'), badge.get('days'))
            if 'transports' in keys:
                transport = values
                diff = 'Annulation de {} vers {} à {} ({}, Nb: {})'.format(transport.get('departure_place'),
                                                  transport.get('arrival_place'), transport.get('departure_time'),
                                                  transport.get('phone'), transport.get('nb_persons'))
                if transport.get('comment'):
                    diff += ' Commentaire: {}'.format(transport.get('comment'))

        return diff
    except Exception as e:
        print('JSON parsing has failed')  # do nothing if translation fails
