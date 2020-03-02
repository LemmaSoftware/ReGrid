# CMG Class Reference

The CMG class can be used to convert CMG formatted grids to VTK grids that can be viewed in Paraview.  It currently supports cartesian and (structured) corner-point grids.  Since CMG files may be formatted in a variety of different ways, errors may occur having to do with format or ordering of keywords in your specific CMG file.  Info on resolving these errors (should they arise) should exist in those locations in the CMG class source code.  

## Getting Started
Clone or download the ReGrid package here:
[https://github.com/LemmaSoftware/ReGrid](https://github.com/LemmaSoftware/ReGrid)

### Dependencies

The ReGrid dependencies include numpy, vtk, pyevtk, and matplotlib.  vtk is not (at the moment) compatible with Python 3.8.  

## Example - Build cartesian grid, read porosity
```python
grid = FlowGrid.CMG()
fname_in = 'input_file.dat'
grid.buildCart(fname_in)
```

## Example - Build corner point grid, read porosity

Initialize CMG grid.

```python
grid = FlowGrid.CMG()
```

Build corner point grid from input (.dat) file.  

```python
fname_in = 'input_file.dat'
grid.buildCorner(fname_in)
```
Read porosity.  The third argument here is the string that signifies the end of the POR property section in the .dat file (this may be different in your .dat file).  This argument tells us when to stop reading in a property and is required if ALL keyword is present next to a property name.  
```python
grid.readProperty(fname_in, '*POR', '**$')
```

## Example - Add output property to grid
readOutputProperty will read the designated property from the .out file for all timesteps it exists for.  The second argument is the (time-series) property we would like to read from an output file as it appears in the output file.  The third argument is the title that this property will have in our vtk file.  
```python
fname_out = 'output_file.out'
grid.readOutputProperty(fname_out, 'Oil Relative Permeability, Kro', 'OilRP')
```
## Example - Export to VTK
```python
grid.exportVTK("./SACROC_CMG_VTK")
```

## Questions?
Please email Alec at anelson@egi.utah.edu

