from .cache import property_cache_forever, property_cache_once_per_frame
from .constants import PYLON
from .position import Point2

import random
import cv2
import numpy as np

import datetime


class Minimap:
    def __init__(
        self,
        game,
        map_scale=2,
        show_heightmap=True,
        show_ramps=False,
        show_vision_blockers=True,
        show_creep=True,
        show_psi=True,
        show_minerals=True,
        show_geysers=True,
        show_xelnaga=True,
        show_destructables=True,
        show_allies=True,
        show_enemies=True,
        show_blips=True,
        show_visibility=False,
        custom_points={},  # {Point2([100, 50]): (200, 50, 50),(Point2([101, 120]),Point2([101, 135]),Point2([101, 150])): (200, 250, 250)}
    ):
        self.game = game
        self.map_scale = map_scale
        self.show_heightmap = show_heightmap
        self.show_ramps = show_ramps
        self.show_vision_blockers = show_vision_blockers
        self.show_creep = show_creep
        self.show_psi = show_psi
        self.show_minerals = show_minerals
        self.show_geysers = show_geysers
        self.show_xelnaga = show_xelnaga
        self.show_destructables = show_destructables
        self.show_allies = show_allies
        self.show_enemies = show_enemies
        self.show_blips = show_blips
        self.show_visibility = show_visibility
        self.custom_points = custom_points

        self.colors = {
            "ally_units": (0, 255, 0),
            "enemy_units": (0, 0, 255),
            "psi": (240, 240, 140),
            "creep": (73, 33, 63),
            "geysers": (60, 160, 100),
            "minerals": (220, 180, 140),
            "destructables": (80, 100, 120),
            "vision_blockers": (0, 0, 0),
            "ramp": (110, 100, 100),
            "upperramp": (120, 110, 110),
            "lowerramp": (100, 90, 90),
            "xelnaga": (170, 200, 100),
        }

    def draw_map(self):
        if self.show_heightmap:
            map_data = np.copy(self.heightmap)
        else:
            map_data = np.copy(self.empty_map)
        if self.show_ramps:
            self.add_ramps(map_data)
        if self.show_vision_blockers:
            map_data = self.add_vision_blockers(map_data)
        if self.show_psi:
            map_data = self.add_creep(map_data)
        if self.show_psi:
            map_data = self.add_psi(map_data)
        if self.show_minerals:
            self.add_minerals(map_data)
        if self.show_geysers:
            self.add_geysers(map_data)
        if self.show_xelnaga:
            self.add_xelnaga(map_data)
        if self.show_destructables:
            self.add_destructables(map_data)
        if self.show_allies:
            self.add_allies(map_data)
        if self.show_enemies:
            self.add_enemies(map_data)
        if self.show_blips:
            self.add_blips(map_data)
        if self.show_blips:
            self.add_blips(map_data)
        self.add_custom_points(map_data)

        flipped = cv2.flip(map_data, 0)
        cv2.imshow("Debug minimap", flipped)
        cv2.waitKey(1)

    @property_cache_forever
    def empty_map(self):
        map_scale = self.map_scale
        map_data = np.zeros(
            (
                self.game.game_info.map_size[1] * map_scale,
                self.game.game_info.map_size[0] * map_scale,
                3,
            ),
            np.uint8,
        )
        return map_data

    @property_cache_forever
    def heightmap(self):
        # gets the min and max heigh of the map for a better contrast
        h_min = np.amin(self.game._game_info.terrain_height.data_numpy)
        h_max = np.amax(self.game._game_info.terrain_height.data_numpy)
        multiplier = 160 / (h_max - h_min)

        map_data = self.empty_map

        for (y, x), h in np.ndenumerate(self.game._game_info.terrain_height.data_numpy):
            color = (h - h_min) * multiplier
            cv2.rectangle(
                map_data,
                (x * self.map_scale, y * self.map_scale),
                (
                    x * self.map_scale + self.map_scale,
                    y * self.map_scale + self.map_scale,
                ),
                (color * 18 / 20, color * 19 / 20, color),
                -1,
            )
        return map_data

    def add_ramps(self, map_data):
        for r in self.game.game_info.map_ramps:
            ramp_point_radius = 0.5
            for p in r.points:
                cv2.rectangle(
                    map_data,
                    (
                        (int(p[0] - ramp_point_radius) * self.map_scale),
                        int((p[1] - ramp_point_radius) * self.map_scale),
                    ),
                    (
                        (int(p[0] + ramp_point_radius) * self.map_scale),
                        int((p[1] + ramp_point_radius) * self.map_scale),
                    ),
                    self.colors["ramp"],
                    -1,
                )
            for p in r.upper:
                cv2.rectangle(
                    map_data,
                    (
                        (int(p[0] - ramp_point_radius) * self.map_scale),
                        int((p[1] - ramp_point_radius) * self.map_scale),
                    ),
                    (
                        (int(p[0] + ramp_point_radius) * self.map_scale),
                        int((p[1] + ramp_point_radius) * self.map_scale),
                    ),
                    self.colors["upperramp"],
                    -1,
                )
            for p in r.lower:
                cv2.rectangle(
                    map_data,
                    (
                        (int(p[0] - ramp_point_radius) * self.map_scale),
                        int((p[1] - ramp_point_radius) * self.map_scale),
                    ),
                    (
                        (int(p[0] + ramp_point_radius) * self.map_scale),
                        int((p[1] + ramp_point_radius) * self.map_scale),
                    ),
                    self.colors["lowerramp"],
                    -1,
                )

    def add_vision_blockers(self, map_data):
        vb = map_data.copy()
        for p in self.game.game_info.vision_blockers:
            vision_blocker_point_radius = 0.5
            cv2.rectangle(
                vb,
                (
                    (int(p[0] - vision_blocker_point_radius) * self.map_scale),
                    int((p[1] - vision_blocker_point_radius) * self.map_scale),
                ),
                (
                    (int(p[0] + vision_blocker_point_radius) * self.map_scale),
                    int((p[1] + vision_blocker_point_radius) * self.map_scale),
                ),
                self.colors["vision_blockers"],
                -1,
            )
        alpha = 0.5  # Transparency factor.

        return cv2.addWeighted(map_data, alpha, vb, 1 - alpha, 0)

    def add_creep(self, map_data):
        creep = map_data.copy()

        for (y, x), v in np.ndenumerate(self.game.state.creep.data_numpy):
            if v:
                cv2.rectangle(
                    map_data,
                    (x * self.map_scale, y * self.map_scale),
                    (
                        x * self.map_scale + self.map_scale,
                        y * self.map_scale + self.map_scale,
                    ),
                    self.colors["creep"],
                    -1,
                )

        alpha = 0.8  # Transparency factor.

        return cv2.addWeighted(map_data, alpha, creep, 1 - alpha, 0)

    def add_psi(self, map_data):
        psi = map_data.copy()

        for psi_provider in self.game.units(PYLON):
            psi_center = psi_provider.position
            psi_radius = 6.5
            cv2.circle(
                map_data,
                (
                    int(psi_center[0] * self.map_scale),
                    int(psi_center[1] * self.map_scale),
                ),
                int(psi_radius * self.map_scale),
                self.colors["psi"],
                -1,
            )

        alpha = 0.3  # Transparency factor.

        return cv2.addWeighted(map_data, alpha, psi, 1 - alpha, 0)

    def add_minerals(self, map_data):
        for mineral in self.game.state.mineral_field:
            mine_pos = mineral.position
            cv2.rectangle(
                map_data,
                (
                    int((mine_pos[0] - 0.75) * self.map_scale),
                    int((mine_pos[1] - 0.25) * self.map_scale),
                ),
                (
                    int((mine_pos[0] + 0.75) * self.map_scale),
                    int((mine_pos[1] + 0.25) * self.map_scale),
                ),
                self.colors["minerals"],
                -1,
            )

    def add_geysers(self, map_data):
        for g in self.game.state.vespene_geyser:
            g_pos = g.position
            cv2.rectangle(
                map_data,
                (
                    int((g_pos[0] - g.radius) * self.map_scale),
                    int((g_pos[1] - g.radius) * self.map_scale),
                ),
                (
                    int((g_pos[0] + g.radius) * self.map_scale),
                    int((g_pos[1] + g.radius) * self.map_scale),
                ),
                self.colors["geysers"],
                -1,
            )

    def add_xelnaga(self, map_data):
        for unit in self.game.state.watchtowers:
            cv2.circle(
                map_data,
                (
                    int(unit.position[0] * self.map_scale),
                    int(unit.position[1] * self.map_scale),
                ),
                int(unit.radius * self.map_scale),
                self.colors["xelnaga"],
                -1,
            )
            cv2.circle(
                map_data,
                (
                    int(unit.position[0] * self.map_scale),
                    int(unit.position[1] * self.map_scale),
                ),
                int(22 * self.map_scale),
                self.colors["xelnaga"],
                1,
            )

    def add_destructables(self, map_data):
        # TODO: make a dictionary that contains all footprints of all destructables to draw them the right way
        for unit in self.game.state.destructables:
            cv2.circle(
                map_data,
                (
                    int(unit.position[0] * self.map_scale),
                    int(unit.position[1] * self.map_scale),
                ),
                int(unit.radius * self.map_scale),
                self.colors["destructables"],
                -1,
            )

    def add_allies(self, map_data):
        for unit in self.game.units:
            if unit.is_structure:
                cv2.rectangle(
                    map_data,
                    (
                        int((unit.position[0] - unit.radius) * self.map_scale),
                        int((unit.position[1] - unit.radius) * self.map_scale),
                    ),
                    (
                        int((unit.position[0] + unit.radius) * self.map_scale),
                        int((unit.position[1] + unit.radius) * self.map_scale),
                    ),
                    self.colors["ally_units"],
                    -1,
                )
            else:
                cv2.circle(
                    map_data,
                    (
                        int(unit.position[0] * self.map_scale),
                        int(unit.position[1] * self.map_scale),
                    ),
                    int(unit.radius * self.map_scale),
                    self.colors["ally_units"],
                    -1,
                )

    def add_enemies(self, map_data):
        for unit in self.game.known_enemy_units:
            if unit.is_structure:
                cv2.rectangle(
                    map_data,
                    (
                        int((unit.position[0] - unit.radius) * self.map_scale),
                        int((unit.position[1] - unit.radius) * self.map_scale),
                    ),
                    (
                        int((unit.position[0] + unit.radius) * self.map_scale),
                        int((unit.position[1] + unit.radius) * self.map_scale),
                    ),
                    self.colors["enemy_units"],
                    -1,
                )
            else:
                cv2.circle(
                    map_data,
                    (
                        int(unit.position[0] * self.map_scale),
                        int(unit.position[1] * self.map_scale),
                    ),
                    int(unit.radius * self.map_scale),
                    (0, 0, 255),
                    -1,
                )

    def add_blips(self, map_data):
        for unit in self.game.state.blips:
            cv2.circle(
                map_data,
                (
                    int(unit.position[0] * self.map_scale),
                    int(unit.position[1] * self.map_scale),
                ),
                1,
                self.colors["enemy_units"],
                -1,
            )
            cv2.circle(
                map_data,
                (
                    int(unit.position[0] * self.map_scale) - 1,
                    int(unit.position[1] * self.map_scale) - 1,
                ),
                1,
                self.colors["enemy_units"],
                -1,
            )
            cv2.circle(
                map_data,
                (
                    int(unit.position[0] * self.map_scale) + 1,
                    int(unit.position[1] * self.map_scale) + 1,
                ),
                1,
                self.colors["enemy_units"],
                -1,
            )
            cv2.circle(
                map_data,
                (
                    int(unit.position[0] * self.map_scale) + 1,
                    int(unit.position[1] * self.map_scale) - 1,
                ),
                1,
                self.colors["enemy_units"],
                -1,
            )
            cv2.circle(
                map_data,
                (
                    int(unit.position[0] * self.map_scale) - 1,
                    int(unit.position[1] * self.map_scale) + 1,
                ),
                1,
                self.colors["enemy_units"],
                -1,
            )

    def add_visibility(self, map_data):
        visibility = map_data.copy()
        # gets the min and max heigh of the map for a better contrast
        v_min = np.amin(self.game.state.visibility.data_numpy)
        v_max = np.amax(self.game.state.visibility.data_numpy)
        multiplier = 255 / (v_max - v_min)

        for (y, x), v in np.ndenumerate(self.game.state.visibility.data_numpy):
            color = (v - v_min) * multiplier
            cv2.rectangle(
                map_data,
                (x * self.map_scale, y * self.map_scale),
                (
                    x * self.map_scale + self.map_scale,
                    y * self.map_scale + self.map_scale,
                ),
                (color, color, color),
                -1,
            )

        alpha = 0.2  # Transparency factor.

        return cv2.addWeighted(map_data, alpha, visibility, 1 - alpha, 0)

    def add_custom_points(self, map_data):
        for pointlist, color in self.custom_points.items():
            if isinstance(pointlist, Point2):
                cv2.circle(
                    map_data,
                    (
                        int(pointlist.position[0] * self.map_scale),
                        int(pointlist.position[1] * self.map_scale),
                    ),
                    self.map_scale,
                    color,
                    -1,
                )
            else:
                for point in pointlist:
                    cv2.circle(
                        map_data,
                        (
                            int(point.position[0] * self.map_scale),
                            int(point.position[1] * self.map_scale),
                        ),
                        self.map_scale,
                        color,
                        -1,
                    )
