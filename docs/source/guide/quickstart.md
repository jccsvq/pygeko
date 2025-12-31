# 💻 Quick Start

## 💻 Basic Workflow


```bash
$ pygeko    # Invoque pygeko REPL

Welcome to pyGEKO-Kriger 0.9.0
    
Classes Kdata, Kgrid and Gplot imported.

Use exit() or Ctrl-D (i.e. EOF) to exit.

--> datafile = get_data_path("montebea.csv") # get path to included datafile
--> kd = Kdata(datafile)

Column names default to "X", "Y" and "Z"
nvec dafaults to: 12 and nork to: 1
Please, adapt these parameter to your problem!

--> kd.x_col = "easting"    # which column of the dataset to use as X
--> kd.y_col = "northing"   # which column of the dataset to use as Y
--> kd.z_col = "heigth"     # which column of the dataset to use as Z

--> kd.analyze()

Generating GIK's for 87 data points...
Mod  | MAE        | RMSE       | Corr     | Status
--------------------------------------------------
0    | 131.0157   | 170.1328   | 0.7599   | OK
1    | 123.0204   | 169.7489   | 0.7600   | OK
2    | 140.0318   | 199.4235   | 0.7002   | OK
3    | 140.0318   | 199.4235   | 0.7002   | OK
4    | 312.3967   | 609.6041   | 0.2972   | OK
5    | 130.0814   | 183.6116   | 0.7321   | OK
6    | 123.0204   | 169.7489   | 0.7600   | OK
7    | 140.0318   | 199.4235   | 0.7002   | OK
8    | 312.3967   | 609.6041   | 0.2972   | OK
9    | 130.0814   | 183.6116   | 0.7321   | OK
10   | 123.0204   | 169.7489   | 0.7600   | OK
11   | 123.0204   | 169.7489   | 0.7600   | OK
12   | 123.0038   | 169.7019   | 0.7601   | OK
13   | 140.0314   | 199.4229   | 0.7002   | OK
14   | 130.0617   | 183.5821   | 0.7322   | OK
15   | 123.0204   | 169.7489   | 0.7600   | OK
16   | 123.0204   | 169.7489   | 0.7600   | OK
17   | 123.0038   | 169.7019   | 0.7601   | OK
18   | 123.0196   | 169.7471   | 0.7600   | OK
19   | 122.9569   | 169.5708   | 0.7604   | OK
20   | 123.0196   | 169.7471   | 0.7600   | OK
21   | 122.9569   | 169.5708   | 0.7604   | OK

Validating best model...
Starting Cross-Validation in 87 points...

--- CROSS-VALIDATION SUMMARY ---
Validated points: 85 / 87
Mean Absolute Error (MAE): 122.9569
Root Mean Square Error (RMSE): 169.5708
Correlation Coefficient: 0.7604

--> kg = Kgrid(kd, 0.0, 1000.0, 0.0, 1400.0, 1000, 1000)   # define estimation window and grid resolution (1000x1000)
--> kg.model = 21                                          # choose model
--> kg.estimate_grid(filename="montebea", preview=False)   # let's go...

[GRID] Generating map with Model #21...
Exporting 1000x1000 grid in parallel to montebea_1_12_mod_21.grd...
Progress: 0%
Progress: 10%
Progress: 20%
Progress: 30%
Progress: 40%
Progress: 50%
Progress: 60%
Progress: 70%
Progress: 80%
Progress: 90%
Export completed. Now writing metadata to montebea_1_12_mod_21.hdr...
Completed.
Completed. Data saved to montebea_1_12_mod_21.grd

--> gp = Gplot("montebea_1_12_mod_21")
montebea_1_12_mod_21 (1000x1000) grid successfully read

--> gp.contourd()

```
![montebea_1_12_mod_21](../_static/montebea_1_12_mod_21_contourc.png)

## 💻 Heatmap, Automation
Instead of using `kd.analyze()` above, you can start an automatic model analysis

```python
config_report = kd.tune(nvec_list=range(8, 17, 2), nork_list=[0, 1, 2])
```

And after a long and boring list of results, it obtains a series of `.gck` files, one for each pair of `nork` and `nvec` values, which it can visualize as a heatmap:

```python

kd.plot_tuning_results(config_report)
```
![gck_heatmap](../_static/gck_tuning_plot.png)

Which will quickly guide you to the best parameters to use for your interpolation (nork = 1, nvec = 14)

## 🔍 Command Line Utility `lsgck` (CLI)

pyGEKO provides the `lsgck` command to keep your workspace organized. No need to open Python to check your results:

```bash
$ lsgck

=====================================================================================================
File                           | Date   | nork  | nvec  | MAE      | RMSE     | CORR     | Model     
-----------------------------------------------------------------------------------------------------
montebea_0_10.gck              | 12-27  | 0     | 10    |  122.407 |  167.426 | 0.765566 | 17        
montebea_0_12.gck              | 12-27  | 0     | 12    |  122.003 |  167.832 | 0.764883 | 12        
montebea_0_14.gck              | 12-27  | 0     | 14    |  121.367 |  167.534 | 0.766684 | 17        
montebea_0_16.gck              | 12-27  | 0     | 16    |  121.629 |  167.959 | 0.765885 | 12        
montebea_0_8.gck               | 12-27  | 0     | 8     |  122.345 |   167.89 | 0.763376 | 18        
montebea_1_10.gck              | 12-27  | 1     | 10    |  124.966 |  167.926 | 0.764731 | 0         
montebea_1_12.gck              | 12-27  | 1     | 12    |  122.957 |  169.571 | 0.760423 | 21        
montebea_1_14.gck              | 12-27  | 1     | 14    |  121.332 |  167.144 | 0.768756 | 21        
montebea_1_16.gck              | 12-27  | 1     | 16    |  121.651 |  167.421 | 0.768497 | 19        
montebea_1_8.gck               | 12-27  | 1     | 8     |  126.446 |  170.101 | 0.754191 | 0         
montebea_2_10.gck              | 12-27  | 2     | 10    |  138.043 |  181.814 | 0.716072 | 0         
montebea_2_12.gck              | 12-27  | 2     | 12    |  129.459 |  173.554 | 0.741762 | 0         
montebea_2_14.gck              | 12-27  | 2     | 14    |  124.783 |  167.688 | 0.762002 | 0         
montebea_2_16.gck              | 12-27  | 2     | 16    |  128.726 |  171.328 | 0.751042 | 0         
montebea_2_8.gck               | 12-27  | 2     | 8     |  129.871 |  171.107 | 0.750874 | 0         
=====================================================================================================
    

```

