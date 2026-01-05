# 📖 Tutorial


## Intro

The functionality of `pyGEKO` is contained in the following classes:

* `Kdata` management and analysis of input data
* `Kgrid` interpolation over a rectangular area (grid)
* `Gplot` basic graphical functions for a quick exploration of `Kgrid` results



## `Kdata` use

### Input data

`Kdata` uses a `CSV` file as input. This file must contain columns with the X and Y coordinates of the points and another with the Z values ​​of the variable to be interpolated. Throughout this tutorial, we will use the test data contained in the `montebea.csv` file, the first rows of which are:

```bash
$ head montebea.csv

id,heigth,easting,northing
1,1430.0,150.0,1278.0
2,1410.0,228.0,1182.0
3,1510.0,292.0,1284.0
4,1795.0,409.0,1350.0
5,1743.0,400.0,1268.0
6,1600.0,378.0,1216.0
7,1815.0,460.0,1219.0
8,1897.0,508.0,1318.0
9,1760.0,549.0,1223.0
```

Create a working directory for your tests and access it with the `cd` command. If you cloned the repository, you have the `montebea.csv` file in `/repositorypath/src/pygeko/testdata` and you can copy it to your working directory. In either case, the file can also be accessed from the installed package, as we will see.





### Basic workflow

The core of `Kdata` is a [`pandas.DataFrame`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) object; in fact, all the arguments used in the creation of a `Kdata` object are passed directly to [`pandas.read_csv()`](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html#pandas.read_csv), so that you can use all the functionality of this method to read your `CSV` files. Furthermore, `Kdata` inherits all the attributes of `pandas.DataFrame` so that you can analyze and modify your data just as you would with `pandas`. Let's proceed to create a `Kdata` object:

If you copied the file `montebea.csv` to your working directory, you can start:

```bash
$ python
Python 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
```

```python
>>> from pygeko.kdata import Kdata
>>> kd = Kdata("montebea.csv")
Column names default to "X", "Y" and "Z"
nvec dafaults to: 12 and nork to: 1
Please, adapt these parameter to your problem!
```

The object `kd` has been created!

But, if you installed the package from `pypi.org` start by:

```python
>>> from pygeko.kdata import Kdata
>>> from pygeko.utils import get_data_path
>>> kd=Kdata(get_data_path("montebea.csv"))
Column names default to "X", "Y" and "Z"
nvec dafaults to: 12 and nork to: 1
Please, adapt these parameter to your problem!
```



> Please note that we received an alert regarding default assumptions made by `Kdata`. We will return to this soon.

> Note also that we could have started the session with the `pygeko` command, in which case both the classes and the `get_data_path` function are pre-imported and we can proceed directly to creating the object.

Let's explore our object:

```python
>>> kd.status

Data properties:
              id       heigth     easting     northing
count  87.000000    87.000000   87.000000    87.000000
mean   44.000000  1455.034483  529.977011   721.977011
std    25.258662   266.054263  287.419836   410.964973
min     1.000000   800.000000   34.000000    42.000000
25%    22.500000  1271.000000  294.500000   372.000000
50%    44.000000  1500.000000  539.000000   682.000000
75%    65.500000  1616.000000  775.000000  1099.000000
max    87.000000  2030.000000  992.000000  1390.000000

Setting:
x_col: X
y_col: Y
z_col: Z
 nork: 1
 nvec: 12
Scale: None


>>> 
```

Our X, Y, and Z data are contained in the `easting`, `northing`, and `height` columns. Let's heed the alert received and inform `Kdata` that we wish to use these columns in our problem:

```python
kd.x_col = "easting"    # which column of the dataset to use as X
kd.y_col = "northing"   # which column of the dataset to use as Y
kd.z_col = "heigth"     # which column of the dataset to use as Z
>>> 
```

Let'us explore again:

```python
>>> kd.status

Data properties:
              id       heigth     easting     northing
count  87.000000    87.000000   87.000000    87.000000
mean   44.000000  1455.034483  529.977011   721.977011
std    25.258662   266.054263  287.419836   410.964973
min     1.000000   800.000000   34.000000    42.000000
25%    22.500000  1271.000000  294.500000   372.000000
50%    44.000000  1500.000000  539.000000   682.000000
75%    65.500000  1616.000000  775.000000  1099.000000
max    87.000000  2030.000000  992.000000  1390.000000

Setting:
x_col: easting
y_col: northing
z_col: heigth
 nork: 1
 nvec: 12
Scale: None


>>> 
```

There were two other default values ​​mentioned in the alert: `nork` and `nvec`

* `nork` polynomial drift order
* `nvec` number of neighbors to use

We could change them using:

```python
>>> kd.nork = 2
>>> kd.nvec = 14
```

but for now we'll leave them as they are.

(If you're curious why these integer variables start with "n", the answer lies in the `Fortran` used by the author in the late 1980s to code this algorithm. See the [`gck` project](https://github.com/jccsvq/gck) for more details.)

We can visualize our data with two previews:

```python
>>> kd.plot()
```

![mbplot](../_static/mbplot.png)

```python
kd.trisurf()
```

![mbtrisurf](../_static/mbtrisurf.png)



### A note on generalized covariance models

The mathematical foundations of the kriging method used in this package, using generalized increments of order *k* and generalized covariance models, are briefly explained in [Topography of the Galactic Disk: Z Structure and Large-Scale Star Formation](https://ui.adsabs.harvard.edu/abs/1991ApJ...378..106A/abstract),work from which this project is inherited (see the [`gck`](https://github.com/jccsvq/gck) project on GitHub if you are curious). The generalized covariance model used is of the form:

$$K(h)=\sum_{k=0}^{4} Z_k\cdot K_k(h)$$

where $Z_k$ are the **model parameters** (`zk` variable in the source files) and $K_k$ are the monomials:

|Monomials|
|---
|$K_0 = \delta (h)$|
|$K_1 = h$|
|$K_2 = h^3$|
|$K_3 = h^5$|
|$K_4 = h^2 \log(h)$|

>$K_0=\delta(h)$ is the *nugget* term with $\delta(0)=1$ and $\delta(h)=0$ for $h>0$.

`pyGEKO` explores the use of the 21 models defined in the table below, where 1 represents the use of each monomial and 0 its exclusion:

|Model Number|$K_0$|$K_1$|$K_2$|$K_3$|$K_4$|
|---|---|---|---|---|---|
|0|1|0|0|0|0|
|1|0|1|0|0|0|
|2|0|0|1|0|0|
|3|0|0|0|1|0|
|4|0|0|0|0|1|
|5|1|1|0|0|0|
|6|1|0|1|0|0|
|7|1|0|0|1|0|
|8|1|0|0|0|1|
|9|0|1|1|0|0|
|10|0|1|0|1|0|
|11|0|1|0|0|1|
|12|0|0|1|1|0|
|13|0|0|1|0|1|
|14|1|1|1|0|0|
|15|1|1|0|1|0|
|16|1|1|0|0|1|
|17|0|1|1|1|0|
|18|0|1|1|0|1|
|19|1|1|1|1|0|
|20|1|1|1|0|1|

### Manual analysis

Once we have created and configured our `Kdata` object, we can proceed to analyze it using the `.analyze()` method. This will generate generalized increments of order *k* from the points and fit the 21 generalized covariance models, testing them by a **leave-one-out cross-validation** method. This method only accepts one boolean parameter to decide whether to present a preview of what the krigin of our data would be with the best model found for the values ​​of `nork` and `nvec` used.

```python
>>> kd.analyze(preview=True) # default for preview is True

Generating GIK's for 87 data points...
Mod  | MAE        | RMSE       | Corr     | Status
--------------------------------------------------
0    | 131.0157   | 170.1328   | 0.7599   | OK
1    | 123.0204   | 169.7489   | 0.7600   | OK
2    | 140.0318   | 199.4235   | 0.7002   | OK
3    | 312.3967   | 609.6041   | 0.2972   | OK
4    | 130.0814   | 183.6116   | 0.7321   | OK
5    | 123.0204   | 169.7489   | 0.7600   | OK
6    | 140.0318   | 199.4235   | 0.7002   | OK
7    | 312.3967   | 609.6041   | 0.2972   | OK
8    | 130.0814   | 183.6116   | 0.7321   | OK
9    | 123.0204   | 169.7489   | 0.7600   | OK
10   | 123.0204   | 169.7489   | 0.7600   | OK
11   | 123.0038   | 169.7019   | 0.7601   | OK
12   | 140.0314   | 199.4229   | 0.7002   | OK
13   | 130.0617   | 183.5821   | 0.7322   | OK
14   | 123.0204   | 169.7489   | 0.7600   | OK
15   | 123.0204   | 169.7489   | 0.7600   | OK
16   | 123.0038   | 169.7019   | 0.7601   | OK
17   | 123.0196   | 169.7471   | 0.7600   | OK
18   | 122.9569   | 169.5708   | 0.7604   | OK
19   | 123.0196   | 169.7471   | 0.7600   | OK
20   | 122.9569   | 169.5708   | 0.7604   | OK

Validating best model...
Starting Cross-Validation in 87 points...

--- CROSS-VALIDATION SUMMARY ---
Validated points: 85 / 87
Mean Absolute Error (MAE): 122.9569
Root Mean Square Error (RMSE): 169.5708
Correlation Coefficient: 0.7604
Interpolating 50x50 grid...
```

The preview image should open in a new window:


![mb_analyze_preview](../_static/mb_analyze_preview.png)

This image is a preview of what you can get with `Kgrid`.

Once you close the image, let'us explore again our object:

```python
>>> kd.status

Data properties:
              id       heigth     easting     northing
count  87.000000    87.000000   87.000000    87.000000
mean   44.000000  1455.034483  529.977011   721.977011
std    25.258662   266.054263  287.419836   410.964973
min     1.000000   800.000000   34.000000    42.000000
25%    22.500000  1271.000000  294.500000   372.000000
50%    44.000000  1500.000000  539.000000   682.000000
75%    65.500000  1616.000000  775.000000  1099.000000
max    87.000000  2030.000000  992.000000  1390.000000

Setting:
x_col: easting
y_col: northing
z_col: heigth
 nork: 1
 nvec: 12
Scale: 134.8

Cross validation data follows:

RANK  | MOD  | MAE        | RMSE       | CORR     | ZK (Coefficients)
----------------------------------------------------------------------------------------------------
★ 1   | 20   | 122.9569   | 169.5708   | 0.7604   | [-2.95e-15 -1.78e+03 3.98e-02 0.00e+00 -1.60e+01]
  2   | 18   | 122.9569   | 169.5708   | 0.7604   | [0.00e+00 -1.78e+03 3.98e-02 0.00e+00 -1.60e+01]
  3   | 16   | 123.0038   | 169.7019   | 0.7601   | [2.01e-16 -4.49e+02 0.00e+00 0.00e+00 -1.07e+00]
  4   | 11   | 123.0038   | 169.7019   | 0.7601   | [0.00e+00 -4.49e+02 0.00e+00 0.00e+00 -1.07e+00]
  5   | 17   | 123.0196   | 169.7471   | 0.7600   | [0.00e+00 -5.34e+02 -1.26e-02 3.89e-08 0.00e+00]
  6   | 19   | 123.0196   | 169.7471   | 0.7600   | [-1.77e-16 -5.34e+02 -1.26e-02 3.89e-08 0.00e+00]
  7   | 9    | 123.0204   | 169.7489   | 0.7600   | [0.00e+00 -2.80e+02 -5.90e-05 0.00e+00 0.00e+00]
  8   | 14   | 123.0204   | 169.7489   | 0.7600   | [4.93e-17 -2.80e+02 -5.90e-05 0.00e+00 0.00e+00]
  9   | 5    | 123.0204   | 169.7489   | 0.7600   | [-5.60e-17 -2.79e+02 0.00e+00 0.00e+00 0.00e+00]
  10  | 1    | 123.0204   | 169.7489   | 0.7600   | [0.00e+00 -2.79e+02 0.00e+00 0.00e+00 0.00e+00]
  11  | 15   | 123.0204   | 169.7489   | 0.7600   | [-2.30e-17 -2.54e+02 0.00e+00 1.23e-08 0.00e+00]
  12  | 10   | 123.0204   | 169.7489   | 0.7600   | [0.00e+00 -2.54e+02 0.00e+00 1.23e-08 0.00e+00]
  13  | 0    | 131.0157   | 170.1328   | 0.7599   | [-2.80e+19 0.00e+00 0.00e+00 0.00e+00 0.00e+00]
  14  | 13   | 130.0617   | 183.5821   | 0.7322   | [0.00e+00 0.00e+00 -3.40e-03 0.00e+00 2.24e+00]
  15  | 4    | 130.0814   | 183.6116   | 0.7321   | [0.00e+00 0.00e+00 0.00e+00 0.00e+00 1.65e+00]
  16  | 8    | 130.0814   | 183.6116   | 0.7321   | [-2.23e-21 0.00e+00 0.00e+00 0.00e+00 1.65e+00]
  17  | 12   | 140.0314   | 199.4229   | 0.7002   | [0.00e+00 0.00e+00 9.23e-03 -2.99e-09 0.00e+00]
  18  | 2    | 140.0318   | 199.4235   | 0.7002   | [0.00e+00 0.00e+00 8.89e-03 0.00e+00 0.00e+00]
  19  | 6    | 140.0318   | 199.4235   | 0.7002   | [-7.68e-26 0.00e+00 8.89e-03 0.00e+00 0.00e+00]
  20  | 3    | 312.3967   | 609.6041   | 0.2972   | [0.00e+00 0.00e+00 0.00e+00 3.38e-08 0.00e+00]
  21  | 7    | 312.3967   | 609.6041   | 0.2972   | [-2.11e-36 0.00e+00 0.00e+00 3.38e-08 0.00e+00]
----------------------------------------------------------------------------------------------------
Best model is #20.


>>> 
```
We observe some changes here. First, there is a "Scale" property that is used in the calculations to stabilize the covariance matrix. Second, we now have the result of adjusting all the models and the indication of the optimum (lowest MAE value), in this case at #20.

`analyze` is a time-intensive function, its cost depending linearly on the number of points in the dataset. To avoid tedious recalculations, you can use the `save` and `restore` methods, which will write the results to a `.gck` file that can be used at any time to reconstruct the `Kdata` object.

```python
>>> kd.save()

[OK] Saved: montebea_1_12.gck
     MAE: 122.95693486762474 | nork: 1 | nvec: 12
>>> 
```

Now let's create a second object using `recover`

```python
>>> kd2=Kdata("montebea.csv")
Column names default to "X", "Y" and "Z"
nvec dafaults to: 12 and nork to: 1
Please, adapt these parameter to your problem!
>>> kd2.restore("montebea_1_12.gck")

[RESTORE] Configuration recovered:
          Model: 20 | nork: 1 | nvec: 12
          Original validation: MAE=122.95693486762474
          KDTree regenerated for 87 points.
>>> 
```

Let'us explore `kd2`:


```python
>>> kd2.status

Data properties:
              id       heigth     easting     northing
count  87.000000    87.000000   87.000000    87.000000
mean   44.000000  1455.034483  529.977011   721.977011
std    25.258662   266.054263  287.419836   410.964973
min     1.000000   800.000000   34.000000    42.000000
25%    22.500000  1271.000000  294.500000   372.000000
50%    44.000000  1500.000000  539.000000   682.000000
75%    65.500000  1616.000000  775.000000  1099.000000
max    87.000000  2030.000000  992.000000  1390.000000

Setting:
x_col: easting
y_col: northing
z_col: heigth
 nork: 1
 nvec: 12
Scale: 134.8

Cross validation data follows:

RANK  | MOD  | MAE        | RMSE       | CORR     | ZK (Coefficients)
----------------------------------------------------------------------------------------------------
★ 1   | 20   | 122.9569   | 169.5708   | 0.7604   | [-2.95e-15 -1.78e+03 3.98e-02 0.00e+00 -1.60e+01]
  2   | 18   | 122.9569   | 169.5708   | 0.7604   | [0.00e+00 -1.78e+03 3.98e-02 0.00e+00 -1.60e+01]
  3   | 16   | 123.0038   | 169.7019   | 0.7601   | [2.01e-16 -4.49e+02 0.00e+00 0.00e+00 -1.07e+00]
  4   | 11   | 123.0038   | 169.7019   | 0.7601   | [0.00e+00 -4.49e+02 0.00e+00 0.00e+00 -1.07e+00]
  5   | 17   | 123.0196   | 169.7471   | 0.7600   | [0.00e+00 -5.34e+02 -1.26e-02 3.89e-08 0.00e+00]
  6   | 19   | 123.0196   | 169.7471   | 0.7600   | [-1.77e-16 -5.34e+02 -1.26e-02 3.89e-08 0.00e+00]
  7   | 9    | 123.0204   | 169.7489   | 0.7600   | [0.00e+00 -2.80e+02 -5.90e-05 0.00e+00 0.00e+00]
  8   | 14   | 123.0204   | 169.7489   | 0.7600   | [4.93e-17 -2.80e+02 -5.90e-05 0.00e+00 0.00e+00]
  9   | 5    | 123.0204   | 169.7489   | 0.7600   | [-5.60e-17 -2.79e+02 0.00e+00 0.00e+00 0.00e+00]
  10  | 1    | 123.0204   | 169.7489   | 0.7600   | [0.00e+00 -2.79e+02 0.00e+00 0.00e+00 0.00e+00]
  11  | 15   | 123.0204   | 169.7489   | 0.7600   | [-2.30e-17 -2.54e+02 0.00e+00 1.23e-08 0.00e+00]
  12  | 10   | 123.0204   | 169.7489   | 0.7600   | [0.00e+00 -2.54e+02 0.00e+00 1.23e-08 0.00e+00]
  13  | 0    | 131.0157   | 170.1328   | 0.7599   | [-2.80e+19 0.00e+00 0.00e+00 0.00e+00 0.00e+00]
  14  | 13   | 130.0617   | 183.5821   | 0.7322   | [0.00e+00 0.00e+00 -3.40e-03 0.00e+00 2.24e+00]
  15  | 4    | 130.0814   | 183.6116   | 0.7321   | [0.00e+00 0.00e+00 0.00e+00 0.00e+00 1.65e+00]
  16  | 8    | 130.0814   | 183.6116   | 0.7321   | [-2.23e-21 0.00e+00 0.00e+00 0.00e+00 1.65e+00]
  17  | 12   | 140.0314   | 199.4229   | 0.7002   | [0.00e+00 0.00e+00 9.23e-03 -2.99e-09 0.00e+00]
  18  | 2    | 140.0318   | 199.4235   | 0.7002   | [0.00e+00 0.00e+00 8.89e-03 0.00e+00 0.00e+00]
  19  | 6    | 140.0318   | 199.4235   | 0.7002   | [-7.68e-26 0.00e+00 8.89e-03 0.00e+00 0.00e+00]
  20  | 3    | 312.3967   | 609.6041   | 0.2972   | [0.00e+00 0.00e+00 0.00e+00 3.38e-08 0.00e+00]
  21  | 7    | 312.3967   | 609.6041   | 0.2972   | [-2.11e-36 0.00e+00 0.00e+00 3.38e-08 0.00e+00]
----------------------------------------------------------------------------------------------------
Best model is #20.


>>> 
```

The object has been reproduced. Let's get rid of `kd2`, as we no longer need it.

```python
>>> del kd2
>>>
``` 

### Analysis automation

The next and final step in this tutorial on `Kdata` is automating the previous analysis. The `.tune()` method allows us to iterate the previous process over a grid of `nork` and `nvec` values ​​and store the results in the corresponding `GCK` files, so we don't have to repeat this time-consuming process in the future.

```python

>>> tune_report = kd.tune(nvec_list=range(8, 17, 2), nork_list=[0, 1, 2])

Starting scan of 15 combinations...
Generating GIK's for 87 data points...

Validating best model...
Starting Cross-Validation in 87 points...

--- CROSS-VALIDATION SUMMARY ---
Validated points: 85 / 87
Mean Absolute Error (MAE): 122.3447
Root Mean Square Error (RMSE): 167.8902
Correlation Coefficient: 0.7634

[OK] Saved: montebea_0_8.gck
     MAE: 122.34469974075041 | nvec: 8
```
a long listing follows ... but you have a progress bar at the botton:

```bash
[TUNING SCAN]: 100%|████████████████████████████| 15/15 [00:08<00:00,  1.83it/s]

```

Now let'us try:

```python

>>> kd.plot_tuning_results(tune_report)


========================================
 TUNING RESULT
========================================
 nork  nvec  model_id        mae       rmse     corr
    0     8        17 122.344700 167.890235 0.763376
    0    10        16 122.407479 167.425868 0.765566
    0    12        11 122.003204 167.831532 0.764883
    0    14        16 121.366692 167.534341 0.766684
    0    16        11 121.629493 167.959133 0.765885
    1     8         0 126.445588 170.100559 0.754191
    1    10         0 124.965882 167.926027 0.764731
    1    12        20 122.956935 169.570788 0.760423
    1    14        20 121.331700 167.144087 0.768756
    1    16        18 121.650653 167.421264 0.768497
    2     8         0 129.870813 171.107253 0.750874
    2    10         0 138.042641 181.813895 0.716072
    2    12         0 129.459237 173.553945 0.741762
    2    14         0 124.783077 167.687974 0.762002
    2    16         0 128.726378 171.327919 0.751042
========================================
Best setting: nork=1.0, nvec=14.0
Minimum MAE: 121.3317 (Model #20)

[RESTORE] Configuration recovered:
          Model: 20 | nork: 1 | nvec: 14
          Original validation: MAE=121.33169956379052
          KDTree regenerated for 87 points.
tune() took: 8.48918890953064 seconds
[PLOT] Heatmap saved to: montebea_tuning.png
```
Now, the saved image opens in a new windows:

![montebea_tuning](../_static/montebea_tuning.png)

Once you close the image, open a new terminal window and let's try:

```bash
$ ls *gck
montebea_0_10.gck  montebea_0_8.gck   montebea_1_16.gck  montebea_2_14.gck
montebea_0_12.gck  montebea_1_10.gck  montebea_1_8.gck   montebea_2_16.gck
montebea_0_14.gck  montebea_1_12.gck  montebea_2_10.gck  montebea_2_8.gck
montebea_0_16.gck  montebea_1_14.gck  montebea_2_12.gck
```

and:

```bash
$ lsgck 
Scanning directory: /home/jesus/Nextcloud/gck/pruebas

=====================================================================================================
File                           | Date   | nork  | nvec  | MAE      | RMSE     | CORR     | Model     
-----------------------------------------------------------------------------------------------------
montebea_0_10.gck              | 01-02  | 0     | 10    |  122.407 |  167.426 | 0.765566 | 16        
montebea_0_12.gck              | 01-02  | 0     | 12    |  122.003 |  167.832 | 0.764883 | 11        
montebea_0_14.gck              | 01-02  | 0     | 14    |  121.367 |  167.534 | 0.766684 | 16        
montebea_0_16.gck              | 01-02  | 0     | 16    |  121.629 |  167.959 | 0.765885 | 11        
montebea_0_8.gck               | 01-02  | 0     | 8     |  122.345 |   167.89 | 0.763376 | 17        
montebea_1_10.gck              | 01-02  | 1     | 10    |  124.966 |  167.926 | 0.764731 | 0         
montebea_1_12.gck              | 01-02  | 1     | 12    |  122.957 |  169.571 | 0.760423 | 20        
montebea_1_14.gck              | 01-02  | 1     | 14    |  121.332 |  167.144 | 0.768756 | 20        
montebea_1_16.gck              | 01-02  | 1     | 16    |  121.651 |  167.421 | 0.768497 | 18        
montebea_1_8.gck               | 01-02  | 1     | 8     |  126.446 |  170.101 | 0.754191 | 0         
montebea_2_10.gck              | 01-02  | 2     | 10    |  138.043 |  181.814 | 0.716072 | 0         
montebea_2_12.gck              | 01-02  | 2     | 12    |  129.459 |  173.554 | 0.741762 | 0         
montebea_2_14.gck              | 01-02  | 2     | 14    |  124.783 |  167.688 | 0.762002 | 0         
montebea_2_16.gck              | 01-02  | 2     | 16    |  128.726 |  171.328 | 0.751042 | 0         
montebea_2_8.gck               | 01-02  | 2     | 8     |  129.871 |  171.107 | 0.750874 | 0         
=====================================================================================================

```



## `Kgrid` use

## `Gplot` use


## CLI utilities

### `pygeko`

### `lsgck`


```bash
$ lsgck -h
usage: lsgck [-h] [-d DIR]

pyGEKO Utility: Scan directory for geospatial data.

options:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  Path to the directory to scan (default: current directory
                     ".")
```

### `png2csv`

```bash
$ png2csv -h
usage: png2csv [-h] [-n SAMPLES] [-o OUTPUT] [-s SEED] [--no-viz] [--invert-y]
               input

Random sample generator for pyGEKO from 16-bit PNG DEMs.

positional arguments:
  input                 Path to the PNG DEM file.

options:
  -h, --help            show this help message and exit
  -n SAMPLES, --samples SAMPLES
                        Number of random samples to generate, defaults to
                        1000.
  -o OUTPUT, --output OUTPUT
                        Output CSV filename.
  -s SEED, --seed SEED  Random seed for reproducibility.
  --no-viz              Turn off the display of sample points.
  --invert-y            Invert the Y axis to match geographical orientation.
```

