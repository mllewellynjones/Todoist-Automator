from todoist.api import TodoistAPI
from .config import API_KEY

class ApiWrapper():
    """Makes it much easier to utilize the standard Todoist API by adding
    the following functionality:

    1) List items by project
    ...
    """

    def __init__(self):
        """Set up the API and sync"""
        self.api = TodoistAPI(API_KEY)
        self.api.sync()

    def commit(self):
        self.api.commit()

    def get_project_id_by_name(self, name):
        """Returns the (new) ID number of a project specified by name

        Currently only returns the first instance of a project where multiple
        have the same name
        """

        for project in self.api.state['projects']:
            if project['name'] == name:
                return project['id']

        return None

    def get_items_in_project(self, project_identifier):
        """Returns the items in a project based on an identifier. This can either
        be an int (in which case it's treated as the project ID) or a string 
        (treated as the project name)
        """

        item_list = []

        if type(project_identifier) == str:
            project_id = self.get_project_id_by_name(project_identifier)
        elif type(project_identifier) == int:
            project_id = project_identifier

        for item in self.api.state['items']:
            if item['project_id'] == project_id and item['checked'] == 0:
                item_list.append(item)

        return item_list


    def get_all_items(self):
        """"Returns every item in Todoist"""
        return self.api.state['items']


    def get_root_items_in_project(self, project_identifier):
        "Returns only the root items from a project, ignoring any subitems"
        complete_item_list = self.get_items_in_project(project_identifier)
        return [item for item in complete_item_list if not item['parent_id']]    


    def get_item_id_from_list_by_name(self, item_name, list_of_items):
        """Returns the numeric ID of a project specified by name from the list
        of items given (e.g. list of items in a project
        """

        for item in list_of_items:
            if item_name in item['content']:
                return item['id']

        return None


    def get_all_subitem_ids_by_id(self, top_item_id):
        """Returns a list of all sub-items below a specific item, to any
        level of nesting"""
        
        subitems = {top_item_id: {}}
        for item in self.api.state['items']:
            if item['parent_id'] == top_item_id and item['checked'] == 0:
                # Get subitems for this new item
                nested_subitems = self.get_all_subitem_ids_by_id(item['id'])
                subitems[top_item_id][item['id']] = nested_subitems[item['id']]

        return subitems


    def copy_item_to_inbox_by_id(self, item_id, child_order=None, parent_id=None):
        """Creates a copy of the item, as well as all subitems, in the inbox"""

        old_item = self.get_item_by_id(item_id)
        subitem_ids = self.get_all_subitem_ids_by_id(item_id)

        new_item = self.api.items.add(old_item['content'],
                                      child_order=child_order,
                                      parent_id=parent_id
                                     )

        for subitem_id in subitem_ids[item_id].keys():
            old_subitem = self.get_item_by_id(subitem_id)
            self.copy_item_to_inbox_by_id(subitem_id,
                                          child_order=old_subitem['child_order'],
                                          parent_id=new_item['id']
                                         )
            
        return None

    def copy_project_contents_to_inbox(self, project_name):
        """Copy all items and sub-items from the first instance of a specified 
        project into the inbox"""
        project_id = self.get_project_id_by_name(project_name)
        root_items = self.get_root_items_in_project(project_id)

        for root_item in root_items:
            self.copy_item_to_inbox_by_id(root_item['id'])

        return None


    def get_item_by_id(self, item_id):
        """Remove unnecessary nesting of results from getting an item by ID"""

        return self.api.items.get(item_id)['item']