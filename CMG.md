# CMG Class Reference

The CMG class can be used to convert CMG formatted grids to VTK grids that can be viewed in Paraview.  It currently supports cartesian and (structured) corner-point grids.  Since CMG files may be formatted in a variety of different ways, errors may occur having to do with format or ordering of keywords in your specific CMG file.  Info on resolving these errors (should they arise) should exist in those locations in the CMG class source code.  

## Getting Started
Clone or download the ReGrid package here:
[https://github.com/LemmaSoftware/ReGrid](https://github.com/LemmaSoftware/ReGrid)

### Dependencies

The ReGrid dependencies include numpy, vtk, pyevtk, and matplotlib.  vtk is not (at the moment) compatible with Python 3.8.  

## Example - Build cartesian grid
Initialize CMG grid object.
```python
grid = FlowGrid.CMG()
```
Specify the name of the CMG file we are building the grid from.  For cartesian grids, you may specify the .dat or the .out file, so long as the grid geometry is defined in the file.
```python
fname_in = 'input_file.dat'
```
Build a cartesian grid.  After this step, the grid geometry has been created and could be exported to VTK.  However, the grid cells would not have any attributes defined in them yet... 
```python
grid.buildCart(fname_in)
```

## Example - Build corner point grid, read porosity/permeability

Initialize CMG grid object. 
```python
grid = FlowGrid.CMG()
```

Specify the name of the CMG file we are building the grid from.  For corner point grids, we must specify a .dat file here, since .out files do not contain complete grid geometry definitions.    
```python
fname_in = 'input_file.dat'
grid.buildCorner(fname_in)
```
Read porosity/permeability.  The second arguments are the CMG keywords as they appear in the .dat file.  
```python
grid.readProperty(fname_in, '*POR')
grid.readProperty(fname_in, '*PERMI')
grid.readProperty(fname_in, '*PERMJ')
grid.readProperty(fname_in, '*PERMK')
```

## Reading output properties from .out files
```python
FlowGrid.readOutputProperty(fname, attr_name, attr_title)
```
This method allows us to read the designated property from the .out file for all timesteps it exists for.  After exporting the VTK file, 
**fname:** output file name
**attr_name:** the (time-series) property we would like to read from an output file as it appears in the output file. 
**attr_title:** the title that we would like to assign this attribute.  After exporting to VTK, cell attributes will appear as **attr_title[timestep]**
## Example - Add output property to grid

```python
fname_out = 'output_file.out'
grid.readOutputProperty(fname_out, 'Oil Relative Permeability, Kro', 'OilRP')
```
## Example - Export to VTK
```python
grid.exportVTK("./vtkGrid")
```

## Questions?
Please email Alec at anelson@egi.utah.edu

