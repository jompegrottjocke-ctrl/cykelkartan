"""Bevara Windows-hjulets DLL-filer och delvewheel-sökvägar."""
from PyInstaller.utils.hooks import collect_delvewheel_libs_directory

datas, binaries = collect_delvewheel_libs_directory('osmium')
