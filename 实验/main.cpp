// RegisterAccessBar - registers or unregisters an appbar. 
// Returns TRUE if successful, or FALSE otherwise. 

// hwndAccessBar - handle to the appbar 
// fRegister - register and unregister flag 

// Global variables 
//     g_uSide - screen edge (defaults to ABE_TOP) 
//     g_fAppRegistered - flag indicating whether the bar is registered 

BOOL RegisterAccessBar(HWND hwndAccessBar, BOOL fRegister)
{
    APPBARDATA abd;

    // An application-defined message identifier
    APPBAR_CALLBACK = (WM_USER + 0x01);

    // Specify the structure size and handle to the appbar. 
    abd.cbSize = sizeof(APPBARDATA);
    abd.hWnd = hwndAccessBar;

    if (fRegister)
    {
        // Provide an identifier for notification messages. 
        abd.uCallbackMessage = APPBAR_CALLBACK;

        // Register the appbar. 
        if (!SHAppBarMessage(ABM_NEW, &abd))
            return FALSE;

        g_uSide = ABE_TOP;       // default edge 
        g_fAppRegistered = TRUE;

    }
    else
    {
        // Unregister the appbar. 
        SHAppBarMessage(ABM_REMOVE, &abd);
        g_fAppRegistered = FALSE;
    }

    return TRUE;
}