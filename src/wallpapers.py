def get_windows_wallpaper():
    import ctypes

    SPI_GETDESKWALLPAPER = 0x73
    buffer_size = 256
    wallpaper = ctypes.create_unicode_buffer(buffer_size)
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_GETDESKWALLPAPER, buffer_size, wallpaper, 0
    )
    return wallpaper.value
