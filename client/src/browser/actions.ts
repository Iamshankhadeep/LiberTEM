import { ActionsUnion, createAction } from "../helpers/actionHelpers";
import { DatasetFormParams, DirectoryListingDetails, FSPlace } from "../messages";

export enum ActionTypes {
    LIST_DIRECTORY = 'BROWSER_LIST_DIRECTORY',
    LIST_FULL_PATH = 'BROWSER_LIST_DIRECTORY_FULL',
    DIRECTORY_LISTING = 'BROWSER_DIRECTORY_LISTING',
    DETECT_PARAMS = 'BROWSER_DETECT_PARAMS',
    PARAMS_DETECTED = 'BROWSER_PARAMS_DETECTED',
    ERROR = 'BROWSER_ERROR',
    OPEN = 'BROWSER_OPEN',
    TOGGLE_STACK = 'BROWSER_TOGGLE_STACK',
    CANCEL = 'BROWSER_CANCEL',
    SELECT = 'BROWSER_SELECT',
    SELECT_FILES = 'BROWSER_SELECT_FILE',
    SELECT_FULL_PATH = 'BROWSER_SELECT_FULL_PATH',
    TOGGLE_FILE = 'TOGGLE_FILE_CHECKBOX',
    SELECT_ALL = 'SELECT_ALL_FILE'
}

export const Actions = {
    list: (path: string, name?: string) => createAction(ActionTypes.LIST_DIRECTORY, { path, name }),
    dirListing: (path: string, dirs: DirectoryListingDetails[], files: DirectoryListingDetails[], drives: string[], places: FSPlace[]) => createAction(ActionTypes.DIRECTORY_LISTING, { path, dirs, files, drives, places }),
    open: () => createAction(ActionTypes.OPEN),
    toggleStack: () => createAction(ActionTypes.TOGGLE_STACK),
    cancel: () => createAction(ActionTypes.CANCEL),
    select: (path: string, name: string) => createAction(ActionTypes.SELECT, { path, name }),
    selectFullPath: (path: string) => createAction(ActionTypes.SELECT_FULL_PATH, { path }),
    error: (msg: string, timestamp: number, id: string) => createAction(ActionTypes.ERROR, { msg, timestamp, id }),
    detectParams: (path: string) => createAction(ActionTypes.DETECT_PARAMS, { path }),
    paramsDetected: (path: string, params: DatasetFormParams) => createAction(ActionTypes.PARAMS_DETECTED, { path, params }),
    toggleFile: (index: number) => createAction(ActionTypes.TOGGLE_FILE, {index}),
    selectAll: () => createAction(ActionTypes.SELECT_ALL),
    selectFiles: () => createAction(ActionTypes.SELECT_FILES),
}

export type Actions = ActionsUnion<typeof Actions>;