import numpy as np
import matplotlib.pyplot as plt

data = np.genfromtxt("NOM_9999_ZrO2_pristine_at_100K_50_ftlrgr.gr", skip_header=1)

plt.plot(data[:, 0], data[:, 1])
plt.show()
