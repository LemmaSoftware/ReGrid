import numpy as np
import matplotlib.pyplot as plt 
from scipy.spatial import ConvexHull
import os
import vtk
from vtk.util.numpy_support import numpy_to_vtk


class FlowGrid():
    def __init__( self ):
        pass
    
    def exportVTK(self, fname):
        """ Saves the SUTRA grid as a VTK structured grid file (.vts)
            fname = the filename it will be saved at, if no extension is given, .vts is appended 
        """
        filename, ext = os.path.splitext(fname)
        if self.GridType == "vtkStructuredGrid":
            sWrite = vtk.vtkXMLStructuredGridWriter()
            sWrite.SetInputData( self.Grid )
            sWrite.SetFileName(filename+".vts")
            sWrite.Write()
        elif self.GridType == "vtkUnstructuredGrid":
            sWrite = vtk.vtkXMLUnstructuredGridWriter()
            sWrite.SetInputData( self.Grid )
            sWrite.SetFileName( filename+".vtu" )
            sWrite.Write()
        else:
            print( "Grid type is not recognized" )


class SUTRA( FlowGrid ):
    """ SUTRA is a USGS flow modelling code.  
    """
    def __init__( self ):
        super(SUTRA,self).__init__()
        nx,ny,nz = 0,0,0 

    def loadNodes( self, fname, nx, ny, nz ):
        """ Reads in the points of the grid, ususally in a file called nodewise
            fname = nodes file 
            nx = number of cells in the easting(x) direction 
            ny = number of cells in the northing (y) direction 
            nz = number of cells in depth, positive up 
            This method results in the generation of a VtkStructuredGrid
        """
        self.nx = nx
        self.ny = ny 
        self.nz = nz

        X = np.loadtxt(fname, comments="#")
        self.points = np.reshape( np.array( (X[:,2], X[:,3], X[:,4]) ).T, (nx, ny, nz, 3))
        
        # work directly with VTK structures
        self.GridType = "vtkStructuredGrid"
        self.Grid = vtk.vtkStructuredGrid()
        self.Grid.SetDimensions(124,88,4)    
        vtk_points = vtk.vtkPoints()
        for iz in range(nz):
            for iy in range(ny):
                for ix in range(nx):
                    vtk_points.InsertNextPoint( self.points[ix,iy,iz][0],\
                                                self.points[ix,iy,iz][1],\
                                                self.points[ix,iy,iz][2]  )
        self.Grid.SetPoints(vtk_points)

    def loadNodesConnections( self, nodes, connections ):
        """ In contrast to the above method, the points and connections can be loaded instead. 
            For non-regular grids this is necessary. This method results in the generation 
            of a vtkUnstructuredGrid. 
            nodes = node file, often called nodewise
            connections = element connections, often called incident
        """
        X = np.loadtxt(nodes, comments="#")
        #                   x       y       z
        points = np.array( (X[:,2], X[:,3], X[:,4]) ).T

        self.GridType = "vtkUnstructuredGrid"
        self.Grid = vtk.vtkUnstructuredGrid()
        vtk_points = vtk.vtkPoints()

        for point in range(np.shape( points )[0]) :
            vtk_points.InsertNextPoint( points[point,0], points[point,1], points[point,2]  )
        self.Grid.SetPoints(vtk_points)

        # Read in the connections, the format is as follows 
        #  nodeid    p0, p1, p2, p3, p4, p5, p6, p7, p8
        C = np.loadtxt(connections, comments="#", skiprows=2, dtype=int)
        for line in range(np.shape(C)[0]):
            idList = vtk.vtkIdList()
            for node in C[line,:][1:] :
                idList.InsertNextId( node-1 )
            self.Grid.InsertNextCell(vtk.VTK_HEXAHEDRON, idList)

    def readPermeability(self, fname, label=("$\kappa_x$", "$\kappa_y$", "$\kappa_z$")):
        """ Reads in SUTRA permeability data 
        """
        k = np.loadtxt(fname, comments="#")
        nr, nc = np.shape(k)
        if self.GridType == "vtkStructuredGrid":
            # Sutra and VTK use opposite ordering 
            k = np.reshape(k, (self.nx-1, self.ny-1, self.nz-1, np.shape(k)[1]))
            k = np.reshape( k, (nr, nc), order='F' )
        kx = vtk.vtkDoubleArray()
        kx.SetName(label[0]) 
        ky = vtk.vtkDoubleArray()
        ky.SetName(label[1]) 
        kz = vtk.vtkDoubleArray()
        kz.SetName(label[2]) 
        for ik, K in enumerate(k):
            kx.InsertNextTuple1( K[2] )
            ky.InsertNextTuple1( K[3] )
            kz.InsertNextTuple1( K[4] )
        self.Grid.GetCellData().AddArray(kx)
        self.Grid.GetCellData().AddArray(ky)
        self.Grid.GetCellData().AddArray(kz)

    def readPorosity(self, fname, label="$\Phi$"):
        phi = np.loadtxt( fname )
        nr, nc = np.shape(phi)
        if self.GridType == "vtkStructuredGrid":
            # Sutra and VTK use opposite ordering 
            phi = np.reshape(phi, (self.nx, self.ny, self.nz, np.shape(phi)[1]))
            phi = np.reshape( phi, (nr, nc), order='F' )
        vphi = vtk.vtkDoubleArray()
        vphi.SetName(label)
        for ik, K in enumerate(phi):
            vphi.InsertNextTuple1( K[5] )
        self.Grid.GetPointData().AddArray(vphi)


