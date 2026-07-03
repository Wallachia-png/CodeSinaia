import json
from pathlib import Path
import struct
from point import Point

class Converter:
	# Class attributes
	__slots__ = (
		"_input_file",  	# text
		"_output_file",  	# text
		"_log_file",		# text
		"_format",			# text
		"__data",			# Point[]
		"__errors",			# text[]
	)

	# Constructor
	def __init__(self, input_file, output_file, log_file):
		self._input_file = input_file
		self._output_file = output_file
		self._log_file = log_file
		self.__data = []
		self.__errors = []

	# region - private parsing methods
	# Check if a point name is valid (non-numeric) and returns it
	def __parse_name(self, point_name):
		try:
			int(point_name)
		except ValueError:
			return point_name
		raise ValueError(f"Invalid Point name ({point_name} must not be numerical)")

	# Check if a point coordinate is valid(numeric)) and returns it
	def __parse_coord(self, coord, point_coord):
		try:
			return int(point_coord)
		except ValueError:
			raise ValueError(f"Invalid number {point_coord} for coordinate {coord}")

	# Parses a Point line into a Point object, or an error message if parsing fails
	def __parse_point(self, line):
		token = "<unknown>"
		try:
			token = line.split("_", 1)[1].split("=", 1)[0]
			point_name = self.__parse_name(token)
			point_x = self.__parse_coord("X", line.split("x=", 1)[1].split(",", 1)[0])
			point_y = self.__parse_coord("Y", line.split("y=", 1)[1].split(")", 1)[0])
			return Point(point_name, point_x, point_y)
		except (IndexError,ValueError) as e:
			return f"Point {token}: {str(e)}"
	# endregion - private parsing methods

	# region - private read methods
	def __read_points(self):
		self.__data = []
		self.__errors = []
		match Path(self._input_file).suffix:
			case ".txt":
				self.__read_points_text()
			case ".tsv":
				self.__read_points_tsv()
			case ".json":
				self.__read_points_json()
			case ".bin":
				self.__read_points_bin()
			case _:
				raise ValueError(f"Input format {self._input_file} not supported.")

	# read points for a text file
	def __read_points_text(self):
		line_number = 0
		f = None
		try:
			f = open(self._input_file, encoding="utf-8")
			for line in f:
				line_number += 1
				# a line looks like 'Point_P16=(x=-196, y=209)'
				# need to extract the name (in between _ and first =) and coordinates
				arg = self.__parse_point(line.strip())
				if type(arg) is Point:
					self.__data.append(arg)
				else:
					self.__errors.append(f"Line {line_number}: {arg}")
		except FileNotFoundError:
			self.__errors.append(f"File {self._input_file} was not found!")
		finally:
			if f:
				f.close()

	# read points from a tsv file
	def __read_points_tsv(self):
		line_number = 0
		with open(self._input_file, encoding="utf-8") as f:
			for line in f:
				line_number += 1
				if line_number == 1:
					# Skip header: Name\tX\tY
					continue
				name, x_raw, y_raw = line.rstrip("\n").split("\t")
				point_name = self.__parse_name(name)
				point_x = self.__parse_coord("X", x_raw)
				point_y = self.__parse_coord("Y", y_raw)
				self.__data.append(Point(point_name, point_x, point_y))

	# read points from a json file
	def __read_points_json(self):
		with open(self._input_file, encoding="utf-8") as f:
			data = json.load(f)
			for item in data:
				point_name = self.__parse_name(str(item["name"]))
				point_x = float(item["x"])
				point_y = float(item["y"])
				self.__data.append(Point(point_name, point_x, point_y))

	# read points from a binary file
	def __read_points_bin(self):
		with open(self._input_file, "rb") as f:
			record_count = struct.unpack("<I", f.read(4))[0]
			for _ in range(record_count):
				name_bytes = bytearray()
				ch = f.read(1)
				while ch != b"\x00":
					name_bytes.extend(ch)
					ch = f.read(1)
				x, y = struct.unpack("<dd", f.read(16))
				self.__data.append(Point(name_bytes.decode("utf-8"), x, y))
	# endregion - private read methods

	# region - private write methods
	# write points to a tsv / json or binary file
	def __write_points(self):
		match Path(self._output_file).suffix:
			case ".tsv":
				with open(self._output_file, "w", encoding="utf-8", newline="") as f:
					f.write("Name\tX\tY\n")
					for point in self.__data:
						f.write(f"{point._name}\t{point._x}\t{point._y}\n")
			case ".json":
				json_data = []
				for point in self.__data:
					json_data.append({"name": point._name, "x": point._x, "y": point._y })
				with open(self._output_file, mode="w", encoding="utf-8") as f:
					json.dump(json_data, f, indent=2)
			case ".bin":
				with open(self._output_file, "wb") as f:
					f.write(struct.pack("<I", len(self.__data)))
					for point in self.__data:
						f.write(point._name.encode("utf-8"))
						f.write(b"\x00")
						f.write(struct.pack("<dd", float(point._x), float(point._y)))
			case _:
				raise ValueError(f"Output format {self._output_file} not supported.")

	# write error logs
	def __write_logs(self):
		with open(self._log_file, "w", encoding="utf-8", newline="\n") as f:
			f.write(f"Loaded {len(self.__data) if self.__data else 0} points. Failed parsing {len(self.__errors) if self.__errors else 0}.\n")
			for log in self.__errors:
				f.write(f"{log}\n")
	# endregion - private write methods

	# Pipeline runner: Data transformation from input to output
	def run(self):
		self.__read_points()
		log = [f"Converted {len(self.__data) if self.__data else 0} Points. Failed parsing {len(self.__errors) if self.__errors else 0}."]
		if self.__errors:
			log.extend(self.__errors)
		self.__write_points()
		self.__write_logs()
		return len(self.__errors)

if __name__ == "__main__":
	processors = [
		Converter("data.txt", "data.tsv", "converter_tsv.log"),
		Converter("data.tsv", "data.json", "converter_json.log"),
		Converter("data.json", "data.bin", "converter_bin.log")
	]

	for processor in processors:
		count = processor.run()	
		print(f"{processor._output_file} : Error count: {count}")
