import json
import os
import ui

from datetime import datetime


def convert_dateformat(date):
    """ convert EX)'2016/9/21' to '2016/09/21'
    """
    target = date.split('/')
    if len(target[1]) == 1:  # month
        target[1] = '0' + target[1]
    if len(target[2]) == 1:  # day
        target[2] = '0' + target[2]
    return "/".join(target)


class MyTableViewDataSource (object):
    def tableview_number_of_rows(self, tableview, section):
        return len(tableview.data_source.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell()
        label = ui.Label()
        label.frame = (0,0,400, 50)
        label.text = tableview.data_source.items[row]
        label.alignment = ui.ALIGN_CENTER
        cell.content_view.add_subview(label)
        return cell

    def tableview_can_delete(self, tableview, section, row):
        # Return True if the user should be able to delete the given row.
        return True

    def tableview_delete(self, tableview, section, row):
        deleted_name = tableview.data_source.items[row]
        self.update_delete(deleted_name[11:])  # [11:] = food name  
        del tableview.data_source.items[row]
        tableview.reload()

    def update_delete(self, deleted_name):
        filepath = os.path.join(os.path.realpath('./'), 'food_items.json')
        with open(filepath, 'r') as f:
            food_items = json.load(f)
            
        for idx, food in enumerate(food_items):
            if food.get('name') == deleted_name:
                del food_items[idx]
                break  # keep dupulicate items

        # UPDATE json data
        os.remove(filepath)
        with open(filepath, 'w') as f:
            json.dump(food_items, f, indent=4)


class FoodList (object):
    def __init__(self):	
        self.view = ui.load_view('FoodList')
        self.view.background_color = "#fcf3d2"
        self.view.present('fullscreen')
        self.view.name = 'FoodList'
        self.table_data_reload(None)

    def date_picker_action(self, sender):
        target_date = sender.date
        expire_date = "{year}/{month}/{day}".format(
            year = target_date.year,
            month = target_date.month,
            day = target_date.day
        )
        return expire_date

    def table_data_reload(self, sender):
        """
        """
        items, expired_items = self.convert_json_to_list()
        # call TableView from FoodList.pyui
        # top_table
        top_table = self.view['top_table']
        top_table.data_source = MyTableViewDataSource()
        top_table.data_source.items = items
        top_table.data_source.delete_enabled = True
        top_table.editing = True
        top_table.allows_selection_during_editing = True

        # expired_table
        expired_table = self.view['expired_table']
        expired_table.data_source = MyTableViewDataSource()
        expired_table.data_source.items = expired_items
        expired_table.data_source.delete_enabled = True
        expired_table.editing = True
        expired_table.allows_selection_during_editing = True

        # refresh table
        top_table.reload_data()
        expired_table.reload_data()

    def convert_json_to_list(self):
        """
        """
        today = datetime.now().strftime('%Y/%m/%d')

        filepath = os.path.join(os.path.realpath('./'), 'food_items.json')
        with open(filepath, 'r') as f:
            food_items = json.load(f)
        list_items = []
        expired_items = []
        for food in food_items:
            expire_date = convert_dateformat(food['expire_date'])
            if expire_date <= today:
                expired_items.append(expire_date + " " + food['name'])
            else:
                list_items.append(expire_date + " " + food['name'])
        return list_items, expired_items

    def insert_item(self, sender):
        """
        """
        filepath = os.path.join(os.path.realpath('./'), 'food_items.json')

        food = self.view['food_field'].text
        expire_date = self.date_picker_action(self.view['datepicker'])

        if not food:
            return
        dic = {'name': food, 'expire_date': expire_date}

        with open(filepath, 'r') as f:
            food_items = json.load(f)
            food_items.append(dic)
        # INSERT item to json
        os.remove(filepath)
        with open(filepath, 'w') as f:
            json.dump(food_items, f, indent=4)
        self.view['food_field'].text = ''		
        self.table_data_reload(None)

    @ui.in_background
    def table_action(self, sender):
        info = sender.items[sender.selected_row]
        print('table_init')


FoodList()
