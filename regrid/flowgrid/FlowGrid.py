import os, io
import numpy as np
from datetime import * 
import getpass 

from mpl_toolkits.mplot3d import axes3d
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt 

import vtk
from vtk.util.numpy_support import numpy_to_vtk

import pkg_resources  # part of setuptools
version = pkg_resources.require("ReGrid")[0].version

f2m = 0.3048 # ft to m

class FlowGrid( object ):
    def __init__( self ):
        self.skip = 0
        self.Prop = {}
    
    def exportVTK(self, fname):
        """ Saves the SUTRA grid as a VTK file, either a VTKStructuredGrid (.vts)
            or a VTKUnstructuredGrid (.vtu) depending on mesh type. 
            fname = the filename it will be saved at, if no extension is given, 
            .vts is appended 
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

    def printCOORDS(self, f, p, fstr):
        MAXL = 132
        #if self.skip:
        #    self.skip -= 1
        #    return fstr
        for point in p:
            up = " %2.2f" %(point)
            if len(fstr) + len(up) > MAXL:
                f.write(fstr + "\n")
                fstr = " "
            fstr += up 
        return fstr
    
    def printAC(self, f, p, N, fstr):
        MAXL = 132
        if N == 1:
            up = " %i" %(p)
        else:
            up = " %i*%i" %(N,p)
        if len(fstr) + len(up) > MAXL:
            f.write(fstr + "\n")
            fstr = " "
        fstr += up 
        return fstr
    
    def printPROP(self, f, p, N, fstr):
        MAXL = 132
        if N == 1:
            #up = " %1.4e" %(p) # standard notation 
            up = " %1.4e" %(p) # scientific notation 
        else:
            up = " %i*%1.4e" %(N,p)
            #up = " %i*%1.4e" %(N,p) # scientific notation 
        if len(fstr) + len(up) > MAXL:
            f.write(fstr + "\n")
            fstr = " "
        fstr += up 
        return fstr

    def exportECL(self, fname):
        """ Saves the file as an ECLIPSE grid. For the purposes of ECLIPSE  
        """
        
        # TODO add consistency of dimensions across the inputs
        self.ne, self.nn, self.nz = np.array(self.Grid.GetDimensions()) - 1 # ECLIPSE 

        filename, ext = os.path.splitext(fname)
        if self.GridType == "vtkStructuredGrid":
            with io.open(filename+".GRDECL", 'w', newline='\r\n') as f:
                f.write('-- Generated [\n')
                f.write('-- Format      : ECLIPSE keywords (grid geometry and properties) (ASCII)\n')
                #f.write('-- Exported by : Petrel 2013.7 (64-bit) Schlumberger\n'
                f.write('-- Exported by : ReGrid v.' + version + "\n")
                f.write('-- User name   : ' + getpass.getuser() + "\n")
                f.write('-- Date        : ' + datetime.now().strftime("%A, %B %d %Y %H:%M:%S") + "\n")
                f.write('-- Project     : ' + "ReGrid project\n")
                f.write('-- Grid        : ' + "Description\n")
                f.write('-- Generated ]\n\n')

                f.write('SPECGRID                               -- Generated : ReGrid\n')
                f.write('  %i %i %i 1 F /\n\n' %(self.ne, self.nn, self.nz) )
                f.write('COORDSYS                               -- Generated : ReGrid\n')
                f.write('  1 4 /\n\n') # what is this line?

                f.write('COORD                                  -- Generated : ReGrid\n')
                nz = self.nz
                fstr = str(" ")

                for iy in range(self.nn):
                    for ix in range(self.ne): 
                        p0 = self.Grid.GetCell(ix, iy, 0).GetPoints().GetPoint(0) 
                        fstr = self.printCOORDS(f, p0, fstr)
                        p1 = self.Grid.GetCell(ix, iy, nz-1).GetPoints().GetPoint(4)  
                        fstr = self.printCOORDS(f, p1, fstr)
                    # outside edge on far x
                    p2 = self.Grid.GetCell(ix, iy, 0).GetPoints().GetPoint(1)  
                    fstr = self.printCOORDS(f, p2, fstr)
                    p3 = self.Grid.GetCell(ix, iy, nz-1).GetPoints().GetPoint(5)  
                    fstr = self.printCOORDS(f, p3, fstr)
                # outside edge on far y 
                for ix in range(self.ne):
                    p8 = self.Grid.GetCell(ix, iy, 0).GetPoints().GetPoint(3)  
                    fstr = self.printCOORDS(f, p8, fstr)
                    p9 = self.Grid.GetCell(ix, iy, nz-1).GetPoints().GetPoint(7)  
                    fstr = self.printCOORDS(f, p9, fstr)
                # outside edge on far northeast
                p14 = self.Grid.GetCell(ix, iy, 0).GetPoints().GetPoint(2)  
                fstr = self.printCOORDS(f, p14, fstr)
                p15 = self.Grid.GetCell(ix, iy, nz-1).GetPoints().GetPoint(6)  
                fstr = self.printCOORDS(f, p15, fstr)
                f.write(fstr)
                fstr = " "
                f.write(" /")
                f.write("\n")
                f.write("\n")

                f.write('ZCORN                                  -- Generated : ReGrid\n')
                for iz in range(self.nz):
                    for iy in range(self.nn):
                        # front face
                        for ix in range(self.ne):
                            p0 = self.Grid.GetCell(ix, iy, iz).GetPoints().GetPoint(0)
                            p1 = self.Grid.GetCell(ix, iy, iz).GetPoints().GetPoint(1)
                            fstr = self.printCOORDS(f, [p0[2]], fstr)
                            fstr = self.printCOORDS(f, [p1[2]], fstr)
                        # back face
                        for ix in range(self.ne):
                            p0 = self.Grid.GetCell(ix, iy, iz).GetPoints().GetPoint(3)
                            p1 = self.Grid.GetCell(ix, iy, iz).GetPoints().GetPoint(2)
                            fstr = self.printCOORDS(f, [p0[2]], fstr)
                            fstr = self.printCOORDS(f, [p1[2]], fstr)
                    # bottom layer 
                    for iy in range(self.nn):
                        # front face
                        for ix in range(self.ne):
                            p0 = self.Grid.GetCell(ix, iy, iz).GetPoints().GetPoint(4)
                            p1 = self.Grid.GetCell(ix, iy, iz).GetPoints().GetPoint(5)
                            fstr = self.printCOORDS(f, [p0[2]], fstr)
                            fstr = self.printCOORDS(f, [p1[2]], fstr)
                        # back face
                        for ix in range(self.ne):
                            p0 = self.Grid.GetCell(ix, iy, iz).GetPoints().GetPoint(7)
                            p1 = self.Grid.GetCell(ix, iy, iz).GetPoints().GetPoint(6)
                            fstr = self.printCOORDS(f, [p0[2]], fstr)
                            fstr = self.printCOORDS(f, [p1[2]], fstr)
                f.write(fstr)
                fstr = " "
                f.write(" /")
                f.write("\n")
                f.write("\n")
                f.write('ACTNUM                                 -- Generated : ReGrid\n')
       
                c = -999
                N = 0  
                for iac in self.ActiveCells.flatten( order='F' ):
                    if iac == c:
                        N += 1
                    else:
                        if c != -999:
                            fstr = self.printAC( f, c, N, fstr )
                        c = iac
                        N = 1  
                fstr = self.printAC( f, c, N, fstr )
                f.write(fstr)
                f.write(" /")
                f.write("\n")
                f.write("\n")
        else:
            print("Only structured grids can be converted to ECLIPSE files")    

    def exportECLPropertyFiles( self, fname ):
        """ Convert any point data to cell data
        """

        # Convert point data to cell data for output
        # verifying if this is necessary or if ECLIPSE can use point attributes
        pointConvert = True
        if pointConvert:
            p2c = vtk.vtkPointDataToCellData( )
            p2c.SetInputDataObject( self.Grid )
            p2c.PassPointDataOn() 
            p2c.Update()
            self.Grid = p2c.GetOutput()

        filename, ext = os.path.splitext(fname)
        for ia in range( self.Grid.GetCellData().GetNumberOfArrays() ):
            prop = self.Grid.GetCellData().GetArray(ia).GetName()        
            print ("exporting prop", prop) 
            if self.GridType == "vtkStructuredGrid":
                with io.open(filename+"prop-"+prop.lower()+".GRDECL", 'w', newline='\r\n') as f:
                    f.write('-- Generated [\n')
                    f.write('-- Format      : ECLIPSE keywords (grid properties) (ASCII)\n')
                    f.write('-- Exported by : ReGrid v.' + version + "\n")
                    f.write('-- User name   : ' + getpass.getuser() + "\n")
                    f.write('-- Date        : ' + datetime.now().strftime("%A, %B %d %Y %H:%M:%S") + "\n")
                    f.write('-- Project     : ' + "ReGrid project\n")
                    f.write('-- Grid        : ' + "Description\n")
                    f.write('-- Unit system : ' + "ECLIPSE-Field\n")
                    f.write('-- Generated ]\n\n')
                    
                    f.write( prop.upper() + '                                 -- Generated : ReGrid\n' )
                    f.write( '-- Property name in Petrel : ' + prop + '\n' )

                    c = -999.9999
                    N = 0  
                    ii = 0
                    fstr = " "
                    for iz in range(self.nz):
                        for iy in range(self.nn):
                            for ix in range(self.ne):
                                #iac = round(self.Grid.GetCellData().GetArray(ia).GetTuple1(ii), 4) 
                                iac = '{:0.4e}'.format( self.Grid.GetCellData().GetArray(ia).GetTuple1(ii) )
                                print (iac)
                                ii += 1
                                if iac == c:
                                    N += 1
                                else:
                                    if c != -999.9999:
                                        fstr = self.printPROP( f, c, N, fstr )
                                    c = eval(iac)
                                    N = 1  
                    fstr = self.printPROP( f, c, N, fstr )
                    f.write(fstr)
                    f.write(" /")
                    f.write("\n")


class GRDECL( FlowGrid ):
    """ GRDECL processes Schlumberger ECLIPSE files
    """
    def __init__( self ):
        super(GRDECL,self).__init__()
        nx,ny,nz = 0,0,0 

    def loadNodes(self, fname):
        """
            Reads I, J(max), K
                  iterates through I, then decriments J, increments K
                  I = easting
                  J = northing
                  K = depth or elevation?
        """
        with open(fname, "r") as fp:

            # Read in the header
            for line in fp:
                item = line.split()
                if len(item) > 0:
                    if item[0] == "SPECGRID":
                        self.SPECGRID = np.array(fp.readline().split()[0:3], dtype=int)
                    if item[0] == "COORDSYS":
                        self.COORDSYS = fp.readline().split() 
                    if item[0] == "COORD":
                        break

            # Read in the coordinates
            self.coords = []
            for line in fp:
                if line.split()[-1] != "/":
                    self.coords += line.split() 
                else:
                    self.coords +=  line.split()[0:-1]
                    break

            # Read in ZCORN
            self.zcorn = []
            for line in fp:
                item = line.split()
                if len(item) > 0:
                    if item[0] == "ZCORN":
                        for line in fp:
                            if line.split()[-1] != "/":
                                self.zcorn += line.split()
                            else:
                                self.zcorn += line.split()[0:-1]
                                break
                if len(self.zcorn) > 0:
                    break

            # Read in (in)active cells
            self.active = []
            for line in fp:
                item = line.split()
                if len(item) > 0:
                    if item[0] == "ACTNUM":
                        for line in fp:
                            if line.split()[-1] != "/":
                                self.active += line.split()
                            else:
                                self.active += line.split()[0:-1]
                                break
 
        self.coords = np.array(self.coords, dtype=float)

                                   # In Petrel...
        self.ne = self.SPECGRID[0] # x  i
        self.nn = self.SPECGRID[1] # y  j
        self.nz = self.SPECGRID[2] # z  k

        # build grid
        self.buildGrid(plot=False)
        self.buildActiveCells(plot=False)
        self.buildZGrid(plot=False)
        self.calculateVolumes(plot=False)

        # Convert to VTK 
        self.GridType = "vtkStructuredGrid"
        self.Grid = vtk.vtkStructuredGrid()
        self.Grid.SetDimensions(self.ne+1, self.nn+1, self.nz+1)    
        vtk_points = vtk.vtkPoints()
        ve = 1.

        for iz in range(self.nz):
            if iz == 0:
                for iy in range(self.nn+1):
                    for ix in range(self.ne+1):
                        vtk_points.InsertNextPoint( self.X0[ix,iy], \
                                                    self.Y0[ix,iy], \
                                               ve * self.ZZT[iz][ix,iy] )
            for iy in range(self.nn+1):
                for ix in range(self.ne+1):
                    vtk_points.InsertNextPoint( self.X0[ix,iy], \
                                                self.Y0[ix,iy], \
                                           ve * self.ZZB[iz][ix,iy] )
        self.Grid.SetPoints(vtk_points)
        
        # Add in active cells
        ac = vtk.vtkIntArray()
        ac.SetName( "ActiveCells" ) 
        for iac in self.ActiveCells.flatten( order='F' ):
            ac.InsertNextTuple1( iac ) 
        self.Grid.GetCellData().AddArray(ac)

    def buildGrid(self, plot=False):
        """
        Topology of COORD mesh, only describes first layer..
         
                  8--------10-------12-------14
                 /|       /|       /|       /|
                / |      / |      / |      / |
               0--------2--------4--------6  |
               |  9-----|--11----|--13----|--15
               | /      | /      | /      | / 
               |/       |/       |/       |/  
               1--------3--------5--------7            7  -->   (2*(NE+1))
                                                      15  -->   (2*(NE+1)*(NN+1))
        """
        
        print ("Constructing grid")
        #print("Grid dims", self.ne, self.nn, self.nz)
        #print("Num points", 2*(self.ne+1)*(self.nn+1)*3, len(self.coords))

        # number of edges
        self.ndx = self.ne+1 
        self.ndy = self.nn+1              
        self.ndz = self.nz+1              
 
        # extract the triplets
        self.points = {}
        self.points["e"] = self.coords[0::3] 
        self.points["n"] = self.coords[1::3] 
        self.points["z"] = self.coords[2::3]
        
        # Here are the coordinates
        self.X0 = np.reshape(self.points["e"][0::2] , (self.ndx,self.ndy), order="F")
        self.Y0 = np.reshape(self.points["n"][0::2] , (self.ndx,self.ndy), order="F")
        self.Z0 = np.reshape(self.points["z"][0::2] , (self.ndx,self.ndy), order="F")
        
        self.X1 = np.reshape(self.points["e"][1::2] , (self.ndx,self.ndy), order="F")
        self.Y1 = np.reshape(self.points["n"][1::2] , (self.ndx,self.ndy), order="F")
        self.Z1 = np.reshape(self.points["z"][1::2] , (self.ndx,self.ndy), order="F")

        # visualize
        if plot:
            print("plotting")
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_wireframe(f2m*self.X0, f2m*self.Y0, f2m*self.Z0, rstride=1, cstride=1)
            ax.plot_wireframe(f2m*self.X1, f2m*self.Y1, f2m*self.Z1, rstride=1, cstride=1)
            plt.show()

    def buildZGrid(self, plot=False):
        """ 
            Petrel provides the ZCORN in a truly arcane ordering--it's awful--and really, the programmers 
            deserve a special place in hell for doing this. The ordering is as follows, for a given plane:
             
             29    36  30   37 31    38 32    39 33    40 34    41 35    42
              _______  _______  ______  _______  _______  _______  _______
             /      / /      / /     / /      / /      / /      / /      /|
            /      / /      / /     / /      / /      / /      / /      / |
           00----01 02----03 04----05 06----07 08----09 10----11 12----13 /
            |  A  | |  B   | |   C  | |   D  | |   E  | |  F   | |   G  |/
           14----15 16----17 18----19 20----21 22----23 24----25 26----27
           
            
            This pattern is then repeated for each depth layer, it isn't that clear, but my ASCII art skills
            are already sufficiently challenged. 
 
        """

        print("Constructing Z corners")

        #self.zcorn = np.array(self.zcorn, dtype=float)
        #temp = np.zeros( ((self.ne+1)*(self.nn+1)*self.nz) )
        temp = []
        count = 0
        for item in self.zcorn:
            if "*" in item:
                ct = (int)(item.split("*")[0])
                vl = (float)(item.split("*")[1])
                temp += np.tile(vl, ct).tolist()
                count += ct
            else:
                temp += [ (float)(item) ]
                count += 1

        #layers = np.resize(temp, (8, self.ne*self.nn*self.nz ))
        layers = np.resize(temp, (self.nz*2, self.ne*self.nn*4))
        """
        plt.plot(newtemp[0,:])                    # TOP     0    0
        plt.plot(newtemp[1,:])       # SAME --    # BOTTOM  0    1
        #plt.plot(newtemp[2,:])      # SAME --    # TOP     1    2

        plt.plot(newtemp[3,:])       # SAME --    # BOTTOM  1    3
        #plt.plot(newtemp[4,:])      # SAME --    # TOP     2    4
        
        plt.plot(newtemp[5,:])       # SAME --    # BOTTOM  2    5
        #plt.plot(newtemp[6,:])      # SAME --    # TOP     3    6
        plt.plot(newtemp[7,:])                    # BOTTOM  3    7
        """
        self.ZZT = {} # zztop ha ha...two year's later this is still funny -TI
        self.ZZB = {}
        for ilay in range(self.nz):
            self.ZZT[ilay] = np.zeros( (self.ndx, self.ndy) )
            self.ZZB[ilay] = np.zeros( (self.ndx, self.ndy) )
            iis = 0
            #plt.plot(layers[ilay*2])
            for iin in range(self.nn):
                nears = {}
                fars = {}
                bnears = {}
                bfars = {}
                for iif in range(2): 
                    # top
                    nears[iif] = layers[ilay*2][iis:iis+2*self.ne][0::2].tolist()
                    fars[iif]  = layers[ilay*2][iis:iis+2*self.ne][1::2].tolist()
                    layers[ilay*2][iis:iis+2*self.ne][0::2] *= 0. # check 
                    layers[ilay*2][iis:iis+2*self.ne][1::2] *= 0.
                    nears[iif].append(fars[iif][-1])
                    fars[iif] = [nears[iif][0]] + fars[iif]
                    # bottom  
                    bnears[iif] = layers[ilay*2+1][iis:iis+2*self.ne][0::2].tolist()
                    bfars[iif]  = layers[ilay*2+1][iis:iis+2*self.ne][1::2].tolist()
                    layers[ilay*2+1][iis:iis+2*self.ne][0::2] *= 0.
                    layers[ilay*2+1][iis:iis+2*self.ne][1::2] *= 0.
                    bnears[iif].append(bfars[iif][-1])
                    bfars[iif] = [bnears[iif][0]] + bfars[iif]
                    # 
                    iis += 2*self.ne

                self.ZZT[ilay][:,iin] = nears[0]  
                self.ZZB[ilay][:,iin] = bnears[0] 
                # NaN mask for visualizing, but can be sort of a pain to deal with
                #imask = np.nonzero( 1-self.ActiveCells[:,iin,ilay] )
                #self.ZZT[ilay][:,iin][1::][imask] = np.nan
                #self.ZZB[ilay][:,iin][1::][imask] = np.nan
                #if self.ActiveCells[0,iin,ilay] == 0:
                    #self.ZZT[ilay][:,iin][0]  = np.nan 
                    #self.ZZB[ilay][:,iin][0]  = np.nan 
                if iin == self.nn-1:
                    self.ZZT[ilay][:,iin+1] = fars[1]
                    self.ZZB[ilay][:,iin+1] = bfars[1]
                    # NaN mask
                    #self.ZZT[ilay][:,iin+1][1::][imask] = np.nan
                    #self.ZZB[ilay][:,iin+1][1::][imask] = np.nan
                    #if self.ActiveCells[0,iin,ilay] == 0:
                    #    self.ZZT[ilay][:,iin+1][0]  = np.nan 
                    #    self.ZZB[ilay][:,iin+1][0]  = np.nan 

        print ("Layers ||", np.linalg.norm(layers), "||")
        #exit()
 
        # visualize
        if plot:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            #ax.plot_wireframe( self.X0, self.Y0, self.Z0, rstride=1, cstride=1)
            
            ax.plot_wireframe( self.X0, self.Y0, self.ZZT[0], rstride=1, cstride=1, color="blue")
            #ax.plot_wireframe( self.X0, self.Y0, self.ZZT[1], rstride=1, cstride=1, color="blue")
            #ax.plot_wireframe( self.X0, self.Y0, self.ZZT[2], rstride=1, cstride=1, color="blue")
            #ax.plot_wireframe( self.X0, self.Y0, self.ZZT[3], rstride=1, cstride=1, color="blue")
            
            #ax.plot_wireframe( self.X0, self.Y0, self.ZZB[3], rstride=1, cstride=1, color="green")
            
            plt.gca().set_xlim( np.min(self.X0), np.max(self.X0) )
            plt.gca().set_ylim( np.max(self.Y0), np.min(self.Y0) )
            #plt.gca().set_zlim( np.max(self.ZZB[3]),  np.min(self.ZZT[0]) )
            plt.gca().set_zlim( 5000, 4000 )
            plt.savefig("mesh.png")
            plt.show()

    def buildActiveCells(self, plot=False):

        print("Constructing active cells")
        self.ActiveCells = np.zeros( (self.ne*self.nn*self.nz), dtype=int )

        count = 0
        for item in self.active:
            if "*" in item:
                ct = (int)(item.split("*")[0])
                vl = (int)(item.split("*")[1])
                self.ActiveCells[count:count+ct] = vl
                count += ct
            else:
                self.ActiveCells[count] = (int)(item)
                count += 1 
        
        self.ActiveCells = np.reshape(self.ActiveCells, (self.ne, self.nn, self.nz), order="F")

        if plot:
            plt.pcolor(self.X0.T, self.Y0.T, self.ActiveCells[:,:,0].T, edgecolors='w', linewidths=.1)
            plt.xlabel("easting")
            plt.ylabel("northing")
            plt.gca().set_xlim( np.min(self.X0), np.max(self.X0) )
            plt.gca().set_ylim( np.max(self.Y0), np.min(self.Y0) )
            plt.gca().xaxis.tick_top()
            plt.gca().xaxis.set_label_position("top")
            plt.show()

    def calculateVolumes(self, plot=False):
        # Iterate over cells, assert that we are dealing with parallelpiped, if so
        #             | u1    u2   u3 |
        #    A = det  | v1    v2   v3 |
        #             | w1    w2   w3 |
        #self.Volumes = 10000*np.random.normal(0,1, (self.ne, self.nn, self.nz) )
        self.Volumes = np.zeros((self.ne, self.nn, self.nz) )
        for iiz in range(self.nz):
            for iie in range(self.ne):
                for iin in range(self.nn):

                    if self.ActiveCells[iie, iin, iiz]:

                        u = np.array( (self.X0[iie  , iin  ], self.Y0[iie  , iin  ], self.ZZT[iiz][iie, iin]) ) - \
                            np.array( (self.X0[iie+1, iin  ], self.Y0[iie+1, iin  ], self.ZZT[iiz][iie, iin]) )

                        v = np.array( (self.X0[iie  , iin  ], self.Y0[iie  , iin  ], self.ZZT[iiz][iie, iin]) ) - \
                            np.array( (self.X0[iie  , iin+1], self.Y0[iie  , iin+1], self.ZZT[iiz][iie, iin]) )

                        w = np.array( (self.X0[iie  , iin  ], self.Y0[iie  , iin  ], self.ZZT[iiz][iie, iin]) ) - \
                            np.array( (self.X0[iie  , iin  ], self.Y0[iie  , iin  ], self.ZZB[iiz][iie, iin]) )
                        if np.any(u!=u) or  np.any(v!=v) or np.any(w!=w):
                            print("NAN!", iie, iin, iiz)
                            exit()
                        V = np.linalg.det( np.array((f2m*u, f2m*v, f2m*w)) )
                        self.Volumes[iie, iin, iiz] = np.abs(V) # in m^3 
                        
        vr =  ((3./(4.*np.pi))*self.Volumes)**(1./3.) # virtual radius, taking into account porosity

        print("Total grid volume: "+ str(np.sum(self.Volumes)) +  " m^3")

    def readProperty(self, fname):
        """ Reads a single property from a file, for time series or multiple properties
            you need to build on this
        """
        temp = []
        with open(fname, "r") as fp:
            for line in fp:
                item = line.split()
                if len(item) > 0:
                    if item[0] != "--":
                        tag = item[0]
                        attribute = fp.readline().split()[-1]
                        self.Prop[tag] = attribute
                        print("loading", attribute)
                        for line in fp:
                            if line.split()[0] != "--":
                                if line.split()[-1] != "/":
                                    temp += line.split()
                                else:
                                    temp += line.split()[0:-1]
                                    break
         
        data = np.zeros( (self.ne*self.nn*self.nz), dtype=float )
        count = 0
        for item in temp:
            if "*" in item:
                ct = (int)(item.split("*")[0])
                vl = (float)(item.split("*")[1])
                data[count:count+ct] = vl
                count += ct
            else:
                data[count] = (float)(item)
                count += 1 
       
        data = np.reshape(data, (self.ne, self.nn, self.nz), order="F")
        
        # Add to VTK grid
        ac = vtk.vtkDoubleArray()
        ac.SetName( attribute ) 
        for iac in data.flatten( order='F' ):
            ac.InsertNextTuple1( iac ) 
        self.Grid.GetCellData().AddArray(ac)

class SUTRA( FlowGrid ):
    """ SUTRA is a USGS flow modelling code.  
    """
    def __init__( self ):
        super(SUTRA,self).__init__()
        nx,ny,nz = 0,0,0 

    def loadNodes( self, fname, nx, ny, nz, ve=-1 ):
        """ Reads in the points of the grid, ususally in a file called nodewise
            fname = nodes file 
            nx = number of cells in the easting(x) direction 
            ny = number of cells in the northing (y) direction 
            nz = number of cells in depth, positive up 
            ve = vertical exaggeration, default is 1 (none)
            This method results in the generation of a VtkStructuredGrid
        """
        self.nx = nx
        self.ny = ny 
        self.nz = nz
        
        self.ActiveCells = np.ones( (self.nx*self.ny*self.nz), dtype=int )

        X = np.loadtxt(fname, comments="#")
        self.points = np.reshape( np.array( (X[:,2], X[:,3], X[:,4]) ).T, (nx, ny, nz, 3))
        
        # work directly with VTK structures
        self.GridType = "vtkStructuredGrid"
        self.Grid = vtk.vtkStructuredGrid()
        self.Grid.SetDimensions(nx,ny,nz)    
        vtk_points = vtk.vtkPoints()
        for iz in range(nz):
            for iy in range(ny):
                for ix in range(nx):
                    vtk_points.InsertNextPoint( self.points[ix,iy,iz][0],\
                                                self.points[ix,iy,iz][1],\
                                           ve * self.points[ix,iy,iz][2]  )
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
            k = np.reshape( k, (self.nx-1, self.ny-1, self.nz-1, np.shape(k)[1]) )
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

    def readPorosity(self, fname, label="phi"): # LaTeX tags work too: $\phi$ 
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
        
    def readPressure(self, fname, ts=2, label="$P$"):
        nnodes = self.nx*self.ny*self.nz
        P = np.loadtxt( fname, comments="#" )[ts*nnodes:(ts+1)*nnodes,:]
        C = np.loadtxt( fname, comments="#" )[ts*nnodes:(ts+1)*nnodes,:]
        nr, nc = np.shape(P)
        if self.GridType == "vtkStructuredGrid":
            # Sutra and VTK use opposite ordering 
            P = np.reshape( P, (self.nx, self.ny, self.nz, np.shape(P)[1]))
            P = np.reshape( P, (nr, nc), order='F' )
            C = np.reshape( C, (self.nx, self.ny, self.nz, np.shape(C)[1]))
            C = np.reshape( C, (nr, nc), order='F' )
        vP = vtk.vtkDoubleArray()
        vP.SetName(label)
        
        vC = vtk.vtkDoubleArray()
        vC.SetName("Concentration")

        for ik in range( nnodes ):
            vP.InsertNextTuple1( P[ik, 3] )
            vC.InsertNextTuple1( C[ik, 4] )
            #vP.InsertNextTuple1( P[2*nnodes+ik, 3] )
        self.Grid.GetPointData().AddArray(vP)
        self.Grid.GetPointData().AddArray(vC)

