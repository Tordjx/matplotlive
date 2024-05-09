#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 Inria

"""Utility functions and classes."""

from typing import Any, Dict, Sequence

import matplotlib
from matplotlib import pyplot as plt


class LivePlot:
    """Live plot using matplotlib."""

    lines: Dict[str, Any]

    def __init__(self, xlim, ylim, ylim_rhs=None, faster: bool = True):
        """Initialize live plot.

        Args:
            xlim: Limits for the x-axis.
            ylim: Limits for left-hand side y-axis.
            ylim_rhs: Limits for the right-hand side y-axis.
            faster: If set, use blitting.
        """
        if faster:  # blitting doesn't work with all matplotlib backends
            matplotlib.use("TkAgg")
        figure, left_axis = plt.subplots()
        left_axis.set_xlim(*xlim)
        left_axis.set_ylim(*ylim)
        right_axis = None
        if ylim_rhs is not None:
            right_axis = left_axis.twinx()
            right_axis.set_ylim(*ylim_rhs)
        plt.show(block=False)
        plt.pause(0.05)
        self.background = None
        self.canvas = figure.canvas
        self.canvas.mpl_connect("draw_event", self.__on_draw)
        self.faster = faster
        self.figure = figure
        self.left_axis = left_axis
        self.lines = {}
        self.right_axis = right_axis

    def add_line(self, name, *args, **kwargs) -> None:
        """Add a line-plot to the left axis.

        Args:
            name: Name to refer to this line, for updates.
            args: Forwarded to ``pyplot.plot``.
            kwargs: Forwarded to ``pyplot.plot``.
        """
        kwargs["animated"] = True
        (line,) = self.left_axis.plot([], *args, **kwargs)
        self.lines[name] = line

    def add_line_right(self, name, *args, **kwargs) -> None:
        """Add a line-plot to the right axis.

        Args:
            name: Name to refer to this line, for updates.
            args: Forwarded to ``pyplot.plot``.
            kwargs: Forwarded to ``pyplot.plot``.
        """
        if self.right_axis is None:
            raise Exception("right-hand side axis not initialized")
        kwargs["animated"] = True
        (line,) = self.right_axis.plot([], *args, **kwargs)
        self.lines[name] = line

    def legend(self, legend: Sequence[str]) -> None:
        """Add a legend to the plot.

        Args:
            legend: Legend.
        """
        self.left_axis.legend(legend)

    def update_line(self, name: str, xdata, ydata) -> None:
        """Update a previously-added line.

        Args:
            name: Name of the line to update.
            xdata: New x-axis data.
            ydata: New y-axis data.
        """
        self.lines[name].set_data(xdata, ydata)

    def __draw_lines(self):
        for line in self.lines.values():
            self.figure.draw_artist(line)

    def __on_draw(self, event):
        if event is not None:
            if event.canvas != self.canvas:
                raise RuntimeError
        self.background = self.canvas.copy_from_bbox(self.figure.bbox)
        self.__draw_lines()

    def update(self) -> None:
        """Update the output figure."""
        if self.background is None:
            self.__on_draw(None)
        elif self.faster:
            self.canvas.restore_region(self.background)
            self.__draw_lines()
            self.canvas.blit(self.figure.bbox)
        else:  # slow mode, if blitting doesn't work
            self.canvas.draw()
        self.canvas.flush_events()
