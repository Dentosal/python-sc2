from sc2.cache import property_cache_forever, property_cache_once_per_frame
from sc2.constants import PYLON

import random
import cv2
import numpy as np

import datetime


class Minimap:
    def __init__(
        self,
        game,
        map_scale=3,
        show_heightmap=True,
        show_ramps=True,
        show_creep=True,
        show_psi=True,
        show_minerals=True,
        show_geysers=True,
        show_destructables=True,
        show_allies=True,
        show_enemies=True,
        show_visibility=False,
    ):
        self.game = game
        self.map_scale = map_scale
        self.show_heightmap = show_heightmap
        self.show_ramps = show_ramps
        self.show_creep = show_creep
        self.show_psi = show_psi
        self.show_minerals = show_minerals
        self.show_geysers = show_geysers
        self.show_destructables = show_destructables
        self.show_allies = show_allies
        self.show_enemies = show_enemies
        self.show_visibility = show_visibility

        self.colors = {
            "ally_units": (0, 255, 0),
            "enemy_units": (0, 0, 255),
            "psi": (240, 240, 140),
            "geysers": (130, 220, 170),
            "minerals": (220, 180, 140),
            "destructables": (80, 100, 120),
            "ramp": (120, 100, 100),
            "upperramp": (160, 140, 140),
            "lowerramp": (100, 80, 80),
        }

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
        multiplier = 150 / (h_max - h_min)

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
                (color, color, color),
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

    def add_visibility(self, map_data):
        visibility = map_data.copy()
        # gets the min and max heigh of the map for a better contrast
        v_min = np.amin(self.game.state.visibility.data_numpy)
        v_max = np.amax(self.game.state.visibility.data_numpy)
        multiplier = 255 / (v_max - v_min)

        for (y, x), v in np.ndenumerate(self.game.state.visibility.data_numpy):
            color = (v - v_min) * multiplier
            if v != v_min and v != v_max:
                print(v_max)
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

    def draw_map(self):
        if self.show_heightmap:
            map_data = np.copy(self.heightmap)
        else:
            map_data = np.copy(self.empty_map)
        if self.show_ramps:
            self.add_ramps(map_data)
        if self.show_psi:
            map_data = self.add_psi(map_data)
        if self.show_minerals:
            self.add_minerals(map_data)
        if self.show_geysers:
            self.add_geysers(map_data)
        if self.show_destructables:
            self.add_destructables(map_data)
        if self.show_allies:
            self.add_allies(map_data)
        if self.show_enemies:
            self.add_enemies(map_data)
        if self.show_visibility:
            map_data = self.add_visibility(map_data)

        # neutral units self.observation.raw_data.units
        # for unit in self.game.state.towers:
        #   cv2.circle(map_data, (int(unit.position[0]*self.map_scale), int(unit.position[1]*self.map_scale)), int(unit.radius*self.map_scale), (0, 250, 250), -1)

        flipped = cv2.flip(map_data, 0)
        resized = flipped  # cv2.resize(flipped, dsize=None, fx=2, fy=2)
        cv2.imshow("Intel", resized)
        cv2.waitKey(1)
