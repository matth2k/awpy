import logging
import os
import subprocess

import xml.etree.ElementTree as ET

from csgo.utils import NpEncoder, check_go_version


class FrameParser:
    """ This class can parse a CSGO demofile to output game data in a logical structure. Accessible via csgo.parser import FrameParser

    Attributes:
        demofile (string) : A string denoting the path to the demo file, which ends in .dem
        log (boolean)     : A boolean denoting if a log will be written. If true, log is written to "csgo_parser.log"
        match_id (string) : A unique demo name/game id
    
    Raises:
        ValueError : Raises a ValueError if the Golang version is lower than 1.14
    """

    def __init__(
        self, demofile="", log=False, match_id="",
    ):
        self.demofile = demofile
        self.match_id = match_id
        self.rounds = []
        self.demo_error = False
        if log:
            logging.basicConfig(
                filename="csgo_parser.log",
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S",
            )
            self.logger = logging.getLogger("CSGODemoParser")
            self.logger.handlers = []
            fh = logging.FileHandler("csgo_parser.log")
            fh.setLevel(logging.INFO)
            self.logger.addHandler(fh)
            self.logger.info(
                "Initialized CSGODemoParser with demofile " + self.demofile
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S",
            )
            self.logger = logging.getLogger("CSGODemoParser")
            self.logger.info(
                "Initialized CSGODemoParser with demofile " + self.demofile
            )
        acceptable_go = check_go_version()
        if not acceptable_go:
            raise ValueError("Go version too low! Needs 1.14.0")

    def _parse_xml(self):
        """ Parse a demofile using the Go script parse_frames.go -- this function takes no arguments

        Returns:
            Returns a written file named match_id.xml
        """
        self.logger.info(
            "Starting CSGO Golang demofile parser, reading in "
            + os.getcwd()
            + "/"
            + self.demofile
        )
        path = os.path.join(os.path.dirname(__file__), "")
        self.logger.info("Running Golang frame parser from " + path)
        with open(self.match_id + ".xml", "w") as f:
            proc = subprocess.Popen(
                [
                    "go",
                    "run",
                    "parse_frames.go",
                    "-demo",
                    os.getcwd() + "/" + self.demofile,
                ],
                stdout=f,
                cwd=path,
            )
            self.logger.info(
                "Demofile parsing complete, output written to " + self.match_id + ".xml"
            )

    def _clean_xml(self):
        """ Clean the XML file from ._parse_xml()

        Returns:
            Returns a written file named match_id.xml
        """
        tree = ET.parse(self.match_id + ".xml")
        game = tree.getroot()
        start_round = 0
        start_round_elem = None
        for i, round_elem in enumerate(game):
            if (
                int(round_elem.attrib["ctScore"]) + int(round_elem.attrib["tScore"])
                == 0
            ):
                print("removing...")
                if start_round < i:
                    game.remove(start_round_elem)
                start_round = i
                start_round_elem = round_elem
        tree.write(open(self.match_id + ".xml", "w"), encoding="unicode")
        self.logger.info("Cleaned the round XML to remove noisy rounds")

    def parse(self):
        """ Parse the given demofile into an XML file of game "frames"

        Returns:
            Returns a written file named match_id.xml
        """
        self._parse_xml()
        self._clean_xml()