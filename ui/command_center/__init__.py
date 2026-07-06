from __future__ import annotations


def get_command_center(*args, **kwargs):
    from ui.command_center.command_center import CommandCenter
    return CommandCenter(*args, **kwargs)


__all__ = ["get_command_center"]
