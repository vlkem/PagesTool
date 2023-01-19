import acm

root = acm.FPageGroup['SalesTradingRoot']
paths = []
all_paths = []

def showMessageBox(type, message):
    shell = acm.UX.SessionManager().Shell()
    acm.UX().Dialogs().MessageBoxOKCancel(shell, type, message)

def get_paths(root, path_till_now=[]):
    path_till_now.append(root.Name())
    if root.Class() != acm.FPageGroup:
        paths.append(path_till_now[1:])
    for g in root.SubGroups():
        get_paths(g, path_till_now[:])
        
def get_all_paths(root, path_till_now=[]):
    path_till_now.append(root.Name())
    all_paths.append(path_till_now[1:])
    for g in root.SubGroups():
        get_all_paths(g, path_till_now[:])

get_paths(root)
get_all_paths(root)

breadcrumb_paths = ['->'.join(path) for path in paths]
all_paths[0] = ['SalesTradingRoot']
breadcrumb_all_paths = ['->'.join(path) for path in all_paths]

def instrument_is_in_pagegroup(instrument, grp):
    return grp.Includes(instrument)

def add_instrument_to_pagegroup(instrument, grp):
    instrGroupMap = acm.FInstrGroupMap.Select01('instrument=%s and group=%s' % (instrument.Oid(), grp.Oid()), None)
    if instrGroupMap:
        print('The InstrGroupMap already exists. None is created.')
        return None
    print('InstrGroupMap does not exist; Creating.')
    instrGroupMap = acm.FInstrGroupMap()
    instrGroupMap.Instrument(instrument)
    instrGroupMap.Group(grp)
    try:
        instrGroupMap.Commit()        
    except RuntimeError as e:
        print('Failed to create FInstrGroupMap for %s in group %s: %s' % (instrument.Name(), grp.Name(), str(e)))
    return instrGroupMap
    
def delete_instrument_from_pagegroup(instrument, grp):
    instrGroupMap = acm.FInstrGroupMap.Select01('instrument=%s and group=%s' % (instrument.Oid(), grp.Oid()), None)
    if instrGroupMap:
        instrGroupMap.Delete()
    
def get_subgroup_by_name(parentNode, groupName):
    if not parentNode:
        return None
    if parentNode.Name() == groupName:
        return parentNode
    for group in parentNode.SubGroups():
        if group.Name() == groupName:
            return group
    return None


def create_group(grp, name):
    subGroup = acm.FPhysInstrGroup()
    subGroup.SuperGroup(grp)
    subGroup.Name(name)
    subGroup.Terminal(1)  # 1 = FPhysInstrGroup
    try:
        subGroup.Commit()
        print('Creating page group %s in %s' % (name, grp.Name()))
    except RuntimeError as e:
        print('Failed to create group %s in group %s: %s' % (name, grp.Name(), str(e)))
    return subGroup

def add_instrument_to_page(instrument, pageGroups):
        parentGroup = root
        group = root
        for subGroupName in pageGroups:
            group = get_subgroup_by_name(parentGroup, subGroupName)        
            if not group:
                group = create_group(parentGroup, subGroupName)
            parentGroup = group
                        
        if not instrument_is_in_pagegroup(instrument, group):
            add_instrument_to_pagegroup(instrument, group)
        return True
    
def delete_instrument_from_page(instrument, pageGroups):
        parentGroup = root
        group = root
        for subGroupName in pageGroups:
            group = get_subgroup_by_name(parentGroup, subGroupName)        
            if not group:
                group = create_group(parentGroup, subGroupName)
            parentGroup = group
                        
        if instrument_is_in_pagegroup(instrument, group):
            delete_instrument_from_pagegroup(instrument, group)
        return True

def action_handler(index, fieldValues):
    print(breadcrumb_paths)
    if ael_variables[3].getValue(fieldValues) == 'Create new page and add to':
        ael_variables[2].enable(1)
        ael_variables[1][3] = breadcrumb_all_paths
    else:
        ael_variables[2].enable(0)
        ael_variables[1][3] = breadcrumb_paths
    return fieldValues
    
import FRunScriptGUI
ael_variables = FRunScriptGUI.AelVariablesHandler([
    ['cbs', 'Convertibles', 'FConvertible', None, None, 1, 1, 'Convertibles', None, 1, None],
    ['path', 'Path', 'string', breadcrumb_paths, breadcrumb_paths[0], 1, 0, 'Path', None, 1, None],
    ['newPageName', 'New Page Folder Name', 'string', None, None, 0, 0, 'Provide a name for a new page folder', None, 0, None],
    ['action', 'Action', 'string', ['Add to', 'Delete from', 'Create new page and add to'], 'Add to', 1, 0, 'Action', action_handler, 1, None]
])

def ael_main(dict):
    cbs = dict['cbs']
    path = dict['path']
    newPageName = dict['newPageName']
    action = dict['action']
    pageGroups = path.split('->')
    if action == 'Add to':
        for cb in cbs:
            add_instrument_to_page(cb, pageGroups)
        showMessageBox('Information', 'Selected Convertibles were added to %s' % path)
    if action == 'Delete from':
        for cb in cbs:
            delete_instrument_from_page(cb, pageGroups)
        showMessageBox('Information', 'Selected Convertibles were deleted from %s' % path)
    if action == 'Create new page and add to':
        pageGroups.append(newPageName)
        for cb in cbs:
            add_instrument_to_page(cb, pageGroups)
        showMessageBox('Information', 'Page has successfully created.\nSelected Convertibles were added to %s' % path)
