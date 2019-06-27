from flask_table import Table, Col, LinkCol
 
class Results(Table):
    classes = ['table table-striped']
    user_id = Col('Id', show=False)
    user_name = Col('Name')
    user_location = Col('Location')
    edit = LinkCol('Edit', 'edit_view', url_kwargs=dict(id='user_id'))
    delete = LinkCol('Delete', 'delete_user', url_kwargs=dict(id='user_id'))