from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QPushButton, QLabel, QDoubleSpinBox, QSpinBox, QLineEdit, QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog
from dataclasses import dataclass
import os
import subprocess

SETTINGS = QSettings("CCO", "PyRMCMon")

@dataclass
class StoGConfig:
    number_of_files: int # Should be 1
    input_filename: str
    Q_min: float
    Q_max: float
    y_offset: float
    y_scale: float
    Q_offset: float
    scaled_sq_name: str
    scaled_gr_name: str
    r_max: float
    r_points: int
    windows_function: bool
    number_density: float
    y_offset_2: float
    try_again: bool # Should be N
    ff: bool # fourier filter
    ff_r_min: float
    ft_sq_name: str
    ft_gr_name: str
    faber_ziman: float
    ft_rmc_fq_name: str
    ft_rmc_gr_name: str
    ft_rmc_dr_name: str
    cutoff: float
    r_min_first: float
    r_max_first: float

    def to_text(self):
        out = ""
        out += f"{self.number_of_files}\n"
        out += f"{self.input_filename}\n"
        out += f"{self.Q_min} {self.Q_max}\n"
        out += f"{self.y_offset} {self.y_scale}\n"
        out += f"{self.Q_offset}\n"
        out += f"{self.scaled_sq_name}\n"
        out += f"{self.scaled_gr_name}\n"
        out += f"{self.r_max}\n"
        out += f"{self.r_points}\n"
        out += f"{"Y" if self.windows_function else "N"}\n"
        out += f"{self.number_density}\n"
        out += f"{self.y_offset_2}\n"
        out += f"{"Y" if self.try_again else "N"}\n"
        out += f"{"Y" if self.ff else "N"}\n"
        out += f"{self.ff_r_min}\n"
        out += f"{self.ft_sq_name}\n"
        out += f"{self.ft_gr_name}\n"
        out += f"{self.faber_ziman}\n"
        out += f"{self.ft_rmc_fq_name}\n"
        out += f"{self.ft_rmc_gr_name}\n"
        out += f"{self.ft_rmc_dr_name}\n"
        out += f"{self.cutoff} {self.r_min_first} {self.r_max_first}\n\n"

        return out


class StoGPage(QWidget):
    def __init__(self):
        super().__init__()

        self.hbox = QHBoxLayout()

        self.controls = StoGControls()

        self.hbox.addWidget(self.controls)

        self.setLayout(self.hbox)


class StoGControls(QWidget):
    def __init__(self):
        super().__init__()

        self.vbox = QVBoxLayout()

        self.rmcprofile_dir_row = QVBoxLayout()

        self.rmcprofile_dir_row_button = QPushButton("Set RMCProfile directory")
        self.rmcprofile_dir_row_button.clicked.connect(self.select_rmc_dialog)
        self.rmcprofile_dir_row_label = QLabel(SETTINGS.value("RMCProfileDir"))
        self.rmcprofile_dir_row.addWidget(self.rmcprofile_dir_row_button)
        self.rmcprofile_dir_row.addWidget(self.rmcprofile_dir_row_label)


        self.input_file_row = QVBoxLayout()

        self.input_file_row_button = QPushButton("Select input")
        self.input_file_row_button.clicked.connect(self.select_input_dialog)
        self.input_file_row_label = QLabel("")
        self.input_file_row.addWidget(self.input_file_row_button)
        self.input_file_row.addWidget(self.input_file_row_label)

        self.output_dir_row = QVBoxLayout()

        self.output_dir_row_button = QPushButton("Select output directory")
        self.output_dir_row_button.clicked.connect(self.select_output_dir_dialog)
        self.output_dir_row_label = QLabel("")
        self.output_dir_row.addWidget(self.output_dir_row_button)
        self.output_dir_row.addWidget(self.output_dir_row_label)

        self.stem_name_row = QHBoxLayout()

        self.stem_name_row_label = QLabel("Stem name")
        self.stem_name_row_input = QLineEdit()
        self.stem_name_row.addWidget(self.stem_name_row_label)
        self.stem_name_row.addWidget(self.stem_name_row_input)

        self.Q_lim_row = QHBoxLayout()

        self.Q_lim_row_min_label = QLabel("Q<sub>min</sub>")
        self.Q_lim_row_min_input = QDoubleSpinBox()
        self.Q_lim_row_min_input.setDecimals(6)
        self.Q_lim_row_min_input.setMaximum(1000)
        self.Q_lim_row_min_input.setValue(0.5)
        self.Q_lim_row.addWidget(self.Q_lim_row_min_label)
        self.Q_lim_row.addWidget(self.Q_lim_row_min_input)

        self.Q_lim_row_max_label = QLabel("Q<sub>max</sub>")
        self.Q_lim_row_max_input = QDoubleSpinBox()
        self.Q_lim_row_max_input.setDecimals(6)
        self.Q_lim_row_max_input.setMaximum(1000)
        self.Q_lim_row_max_input.setValue(30)
        self.Q_lim_row.addWidget(self.Q_lim_row_max_label)
        self.Q_lim_row.addWidget(self.Q_lim_row_max_input)

        self.Q_lim_row.addStretch(1)

        self.scale_offset_row = QHBoxLayout()

        self.scale_offset_row_offset_label = QLabel("Offset")
        self.scale_offset_row_offset_input = QDoubleSpinBox()
        self.scale_offset_row_offset_input.setDecimals(6)
        self.scale_offset_row_offset_input.setMaximum(1000)
        self.scale_offset_row_offset_input.setMinimum(-1000)
        self.scale_offset_row_offset_input.setValue(0)
        self.scale_offset_row.addWidget(self.scale_offset_row_offset_label)
        self.scale_offset_row.addWidget(self.scale_offset_row_offset_input)

        self.scale_offset_row_scale_label = QLabel("Scale")
        self.scale_offset_row_scale_input = QDoubleSpinBox()
        self.scale_offset_row_scale_input.setDecimals(6)
        self.scale_offset_row_scale_input.setMaximum(1000)
        self.scale_offset_row_scale_input.setMinimum(-1000)
        self.scale_offset_row_scale_input.setValue(1)
        self.scale_offset_row.addWidget(self.scale_offset_row_scale_label)
        self.scale_offset_row.addWidget(self.scale_offset_row_scale_input)

        self.scale_offset_row.addStretch(1)

        self.Q_offset_row = QHBoxLayout()

        self.Q_offset_row_label = QLabel("Q<sub>offset</sub>")
        self.Q_offset_row_input = QDoubleSpinBox()
        self.Q_offset_row_input.setDecimals(6)
        self.Q_offset_row_input.setMaximum(1000)
        self.Q_offset_row_input.setMinimum(-1000)
        self.Q_offset_row_input.setValue(0)
        self.Q_offset_row.addWidget(self.Q_offset_row_label)
        self.Q_offset_row.addWidget(self.Q_offset_row_input)
        self.Q_offset_row.addStretch(1)

        self.r_max_row = QHBoxLayout()

        self.r_max_row_label = QLabel("r<sub>max</sub>")
        self.r_max_row_input = QDoubleSpinBox()
        self.r_max_row_input.setDecimals(6)
        self.r_max_row_input.setMaximum(1000)
        self.r_max_row_input.setMinimum(-1000)
        self.r_max_row_input.setValue(50)
        self.r_max_row.addWidget(self.r_max_row_label)
        self.r_max_row.addWidget(self.r_max_row_input)
        self.r_max_row.addStretch(1)

        self.r_point_row = QHBoxLayout()

        self.r_point_row_label = QLabel("Number of r points")
        self.r_point_row_input = QSpinBox()
        self.r_point_row_input.setMaximum(100000000)
        self.r_point_row_input.setMinimum(0)
        self.r_point_row_input.setValue(5000)
        self.r_point_row.addWidget(self.r_point_row_label)
        self.r_point_row.addWidget(self.r_point_row_input)
        self.r_point_row.addStretch(1)

        self.windows_function_row = QHBoxLayout()

        self.windows_function_row_checkbox = QCheckBox()
        self.windows_function_row_label = QLabel("Windows function")
        self.windows_function_row.addWidget(self.windows_function_row_checkbox)
        self.windows_function_row.addWidget(self.windows_function_row_label)
        self.windows_function_row.addStretch(1)

        self.number_density_row = QHBoxLayout()

        self.number_density_row_label = QLabel(r"Number density [#/Å<sup>3</sup>]")
        self.number_density_row_input = QDoubleSpinBox()
        self.number_density_row_input.setDecimals(6)
        self.number_density_row_input.setMaximum(1000)
        self.number_density_row_input.setMinimum(-1000)
        self.number_density_row_input.setValue(0.08)
        self.number_density_row.addWidget(self.number_density_row_label)
        self.number_density_row.addWidget(self.number_density_row_input)
        self.number_density_row.addStretch(1)

        self.yoffset2_row = QHBoxLayout()
        self.yoffset2_row_label = QLabel("Y offset 2")
        self.yoffset2_row_input = QDoubleSpinBox()
        self.yoffset2_row_input.setDecimals(6)
        self.yoffset2_row_input.setMaximum(1000)
        self.yoffset2_row_input.setMinimum(-1000)
        self.yoffset2_row_input.setValue(0)
        self.yoffset2_row.addWidget(self.yoffset2_row_label)
        self.yoffset2_row.addWidget(self.yoffset2_row_input)
        self.yoffset2_row.addStretch(1)

        self.fourier_filter_row = QHBoxLayout()

        self.fourier_filter_row_checkbox = QCheckBox()
        self.fourier_filter_row_checkbox.setChecked(True)
        self.fourier_filter_row_label = QLabel("Fourier filter")
        self.fourier_filter_row_cutoff_label = QLabel("r<sub>cutoff</sub>")
        self.fourier_filter_row_cutoff_input = QDoubleSpinBox()
        self.fourier_filter_row_cutoff_input.setDecimals(6)
        self.fourier_filter_row_cutoff_input.setMaximum(1000)
        self.fourier_filter_row_cutoff_input.setMinimum(-1000)
        self.fourier_filter_row_cutoff_input.setValue(0)
        self.fourier_filter_row.addWidget(self.fourier_filter_row_checkbox)
        self.fourier_filter_row.addWidget(self.fourier_filter_row_label)
        self.fourier_filter_row.addWidget(self.fourier_filter_row_cutoff_label)
        self.fourier_filter_row.addWidget(self.fourier_filter_row_cutoff_input)
        self.fourier_filter_row.addStretch(1)

        self.faber_ziman_row = QHBoxLayout()

        self.faber_ziman_row = QHBoxLayout()
        self.faber_ziman_row_label = QLabel("Faber-Ziman coefficient")
        self.faber_ziman_row_input = QDoubleSpinBox()
        self.faber_ziman_row_input.setDecimals(6)
        self.faber_ziman_row_input.setMaximum(1000)
        self.faber_ziman_row_input.setMinimum(-1000)
        self.faber_ziman_row_input.setValue(0.08)
        self.faber_ziman_row.addWidget(self.faber_ziman_row_label)
        self.faber_ziman_row.addWidget(self.faber_ziman_row_input)
        self.faber_ziman_row.addStretch(1)

        self.ripple_row = QHBoxLayout()

        self.ripple_row_cutoff_label = QLabel("Cutoff")
        self.ripple_row_cutoff_input = QDoubleSpinBox()
        self.ripple_row_cutoff_input.setDecimals(6)
        self.ripple_row_cutoff_input.setMaximum(1000)
        self.ripple_row_cutoff_input.setMinimum(-1000)
        self.ripple_row_cutoff_input.setValue(1)

        self.ripple_row_min_label = QLabel("r<sub>min</sub> of 1<sup>st</sup> peak")
        self.ripple_row_min_input = QDoubleSpinBox()
        self.ripple_row_min_input.setDecimals(6)
        self.ripple_row_min_input.setMaximum(1000)
        self.ripple_row_min_input.setMinimum(-1000)
        self.ripple_row_min_input.setValue(2)

        self.ripple_row_max_label = QLabel("r<sub>max</sub> of 1<sup>st</sup> peak")
        self.ripple_row_max_input = QDoubleSpinBox()
        self.ripple_row_max_input.setDecimals(6)
        self.ripple_row_max_input.setMaximum(1000)
        self.ripple_row_max_input.setMinimum(-1000)
        self.ripple_row_max_input.setValue(3)

        self.ripple_row.addWidget(self.ripple_row_cutoff_label)
        self.ripple_row.addWidget(self.ripple_row_cutoff_input)
        self.ripple_row.addWidget(self.ripple_row_min_label)
        self.ripple_row.addWidget(self.ripple_row_min_input)
        self.ripple_row.addWidget(self.ripple_row_max_label)
        self.ripple_row.addWidget(self.ripple_row_max_input)
        self.ripple_row.addStretch(1)

        self.run_stog_button = QPushButton("Run StoG")
        self.run_stog_button.clicked.connect(self.run_stog)

        self.vbox.addLayout(self.rmcprofile_dir_row)
        self.vbox.addLayout(self.input_file_row)
        self.vbox.addLayout(self.output_dir_row)
        self.vbox.addLayout(self.stem_name_row)
        self.vbox.addLayout(self.Q_lim_row)
        self.vbox.addLayout(self.scale_offset_row)
        self.vbox.addLayout(self.Q_offset_row)
        self.vbox.addLayout(self.r_max_row)
        self.vbox.addLayout(self.r_point_row)
        self.vbox.addLayout(self.windows_function_row)
        self.vbox.addLayout(self.number_density_row)
        self.vbox.addLayout(self.yoffset2_row)
        self.vbox.addLayout(self.fourier_filter_row)
        self.vbox.addLayout(self.faber_ziman_row)
        self.vbox.addLayout(self.ripple_row)
        self.vbox.addWidget(self.run_stog_button)
        self.vbox.addStretch(1)


        self.setLayout(self.vbox)

    def select_rmc_dialog(self):
        temp_output = ["", ""]
        temp_output = QFileDialog.getExistingDirectory(self, "Select RMCProfile directory")

        if temp_output == "":
            return

        SETTINGS.setValue("RMCProfileDir", temp_output)
        self.rmcprofile_dir_row_label.setText(temp_output)


    def select_input_dialog(self):
        temp_input_filename = QFileDialog.getOpenFileName(self, "Select input S(Q) file")
        if temp_input_filename[0] == "":
            return

        self.input_filename = temp_input_filename[0]
        self.input_file_row_label.setText(self.input_filename)

    def select_output_dir_dialog(self):
        temp_output = ["", ""]
        if hasattr(self, "input_filename"):
            temp_output = QFileDialog.getExistingDirectory(self, "Select output directory",
                                                           os.path.dirname(self.input_filename))
        else:
            temp_output = QFileDialog.getExistingDirectory(self, "Select output directory")

        if temp_output == "":
            return
        self.output_dir = temp_output
        self.output_dir_row_label.setText(self.output_dir)

    def run_stog(self):
        stem = self.stem_name_row_input.text()

        input_relpath = os.path.relpath(self.input_filename, self.output_dir)

        conf = StoGConfig(
            1,
            input_relpath,
            self.Q_lim_row_min_input.value(),
            self.Q_lim_row_max_input.value(),
            self.scale_offset_row_offset_input.value(),
            self.scale_offset_row_scale_input.value(),
            self.Q_offset_row_input.value(),
            f"{stem}_scaled.sq",
            f"{stem}_scaled.gr",
            self.r_max_row_input.value(),
            self.r_point_row_input.value(),
            self.windows_function_row_checkbox.isChecked(),
            self.number_density_row_input.value(),
            self.yoffset2_row_input.value(),
            False,
            self.fourier_filter_row_checkbox.isChecked(),
            self.fourier_filter_row_cutoff_input.value(),
            f"{stem}_ft.sq",
            f"{stem}_ft.gr",
            self.faber_ziman_row_input.value(),
            f"{stem}_ft_rmc.fq",
            f"{stem}_ft_rmc.gr",
            f"{stem}_ft_rmc.dr",
            self.ripple_row_cutoff_input.value(),
            self.ripple_row_min_input.value(),
            self.ripple_row_max_input.value(),
        )

        rmc_dir = SETTINGS.value("RMCProfileDir")
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = f"{rmc_dir}/exe/libs"
        env["LIBRARY_PATH"] = f"{rmc_dir}/exe/libs"
        res = subprocess.run([f"{rmc_dir}/exe/stog_new"],
                             input=conf.to_text(), text=True, env=env,
                             cwd=self.output_dir)

        print(f"{SETTINGS.value("RMCProfileDir")}/exe/stog_new")

        print(conf.to_text())
        print(res)
        print(res.stdout)
        pass


