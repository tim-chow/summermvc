is_tornado_installed = True

try:
    import tornado
except ImportError:
    is_tornado_installed = False

