/* 
CalculateACV.java

Java class CalculateACV 
Calculates  and outputs the Average Cumulative Visibility (ACV) 
of an SRTM tile to standard out.

How to use:
 javac CalcuateACV.java 
 java CalculateACV SRTM_Terrain/N37W122.hgt 100 100 0 0
   Calculates ACV for SRTM tile N37W122.hgt (assuming it is in the SRTM_Terrain folder),
   sets the east width to 100, the south width to 100, the east offset to 0, and
   the south offset to 0.
 
Author: Sam Mansfield
*/

import java.io.*;
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;

public class CalculateACV {
  
  public static void main(String[] args) {
    String filename = args[0];
    int ew = Integer.parseInt(args[1]);
    int sw = Integer.parseInt(args[2]);
    int eo = Integer.parseInt(args[3]);
    int so = Integer.parseInt(args[4]);
    double visibility = 0.0;
    double perfectVisibility = ew*sw - 1;
    DescriptiveStatistics stats = new DescriptiveStatistics(); 

    Terrain terrain = new Terrain(filename, ew, sw, eo, so);

    for(int i = 0; i < ew; i++) {
      for(int j = 0; j < sw; j++) {
        terrain.calculateLOS(i, j);
        visibility = 0.0;
        for(int k = 0; k < ew; k++) {
          for(int l = 0; l < sw; l++) {
            if(k != i || l != j) {
              if(terrain.isThereLOS(k, l)) {
                visibility++;
              }
            }
          }
        }
        stats.addValue(visibility*100/perfectVisibility);
      }
    }
    
    //System.out.println(filename + ", ew: " + ew + ", sw: " + sw + ", (" + eo + ", " + so + "), " 
    //  + new Double(visibility*100.0/perfectVisibility) + "%"); 
    System.out.println(filename + ", ew: " + ew + ", sw: " + sw + ", (" + eo + ", " + so + "), " 
      + stats.getMean() + "%, " + stats.getStandardDeviation()); 
  }


  public static class Terrain {
    /* The heights of the current map. */
    public double h[][];
    /* The source location. */
    private int srcX = -1;
    private int srcY = -1;
    /* The calculated viewshed based on srcX and srcY. */
    public double los[][];
    /* Used to determine color gradient. */
    public double min = 32768.0;
    public double max = -1.0;
    /* The width and height of an hgt file. Although technically it is 3601, but
     * the extra byte is dupblicated in adjacent tiles.
     */
    private int HGTWIDTH = 3600;
    private int HGTHEIGHT = 3600;
  
    /* The filepath of the terrain file. If empty a well terrain will be
     * used instead. 
     */
    public String TERRAIN_FILEPATH = "";
    /* The width (degrees) extending to the East TerrainLOS 
     * uses of the terrain file. 
     */
    public int EAST_WIDTH = 100;
    /* The width (degrees) extending to the South TerrainLOS 
     * uses of the terrain file. 
     */
    public int SOUTH_WIDTH = 100;
    /* The offset (degrees( to the East TerrainLOS will start 
     * reading the terrain file. 
     */
    public int EAST_OFFSET = 0;
    /* The offset (degrees) to the South TerrainLOS will start 
     * reading the terrain file. 
     */
    public int SOUTH_OFFSET = 0;
  
    /* A new terrain takes in a filepath, East width, South width,
     * East offset, and South Offset. If filepath is "" then a synthetic
     * well terrain is used instead.
     */
    public Terrain(String fp, int ew, int sw, int eo, int so) {
      TERRAIN_FILEPATH = fp;
      EAST_WIDTH = ew;
      SOUTH_WIDTH = sw;
      EAST_OFFSET = eo;
      SOUTH_OFFSET = so;
  
      configureMap();
    }
   
    /* Configures the map using the current set configurations */
    public void configureMap() {
      /* Error Checking */
      if(EAST_WIDTH < 0 || SOUTH_WIDTH < 0 || 
         EAST_OFFSET < 0 || SOUTH_OFFSET < 0) {
        System.out.println("All widths and offsets must be greater than or equal to 0" +
                     " EAST_WIDTH: " + EAST_WIDTH + "SOUTH_WIDTH: " + SOUTH_WIDTH +  
                     "\nEAST_OFFSET: " + EAST_OFFSET + " SOUTH_OFFSET: " + SOUTH_OFFSET);
      }
      if((EAST_WIDTH + EAST_OFFSET) > HGTWIDTH) {
        System.out.println("East width plus East offset must be less than 3600" +
                     "\nEAST_WIDTH: " + EAST_WIDTH + " EAST_OFFSET: " + EAST_OFFSET);
      }
      if((SOUTH_WIDTH + SOUTH_OFFSET) > HGTHEIGHT) {
        System.out.println("South width plus South offset must be less than 3600" +
                     "\nSOUTH_WIDTH: " + SOUTH_WIDTH + " SOUTH_OFFSET: " + SOUTH_OFFSET);
      }
     
      /* TODO: Why plus 1? */
      h = new double[EAST_WIDTH][SOUTH_WIDTH];
      los = new double[EAST_WIDTH][SOUTH_WIDTH];
      
      //byte buffer;
      /* Set these as the lowest respective possible values. Each height is a signed
       * two byte value, so the possbile range is -32767 to 32767. TerrainLOS currently
       * only supports positive heights so the range is 0 to 32767. */
      min = 32768.0;
      max = -1.0;
      
      if(TERRAIN_FILEPATH != "") {
        try {
          FileInputStream inputStream = new FileInputStream(TERRAIN_FILEPATH);
  
          int skip_rows = 3601 - SOUTH_WIDTH - SOUTH_OFFSET;
          int skip_cols = 3601 - EAST_WIDTH - EAST_OFFSET;
          int msb;
          int lsb;
          int xi;
          int yi;
          double elevation;
  
          inputStream.skip(SOUTH_OFFSET*2*3601);
          yi = 0;
          for(int mapY = SOUTH_OFFSET; mapY < SOUTH_WIDTH + SOUTH_OFFSET; mapY++) {
            inputStream.skip(EAST_OFFSET*2);
            xi = 0;
            for(int mapX = EAST_OFFSET; mapX < EAST_WIDTH + EAST_OFFSET; mapX++) { 
              msb = inputStream.read();
              lsb = inputStream.read();
              /* By default each byte is treated as signed, so convert back to the
               * unisnged value if negative. 
               */
              if(msb < 0) msb += 256;
              if(lsb < 0) msb += 256;
              elevation = twosComp((msb << 8) + lsb, 16);
              if(elevation > 0) {
                h[xi][yi] = elevation;
              }
              else {
                elevation = 0;
              }
              if(max < ((double) elevation)) {
                max = (double) elevation; 
              }
              if(min > ((double) elevation)) {
                min = (double) elevation;
              }
              xi++;
            }
            inputStream.skip(skip_cols*2);
            yi++;
          }
          inputStream.skip(skip_rows*2*3601);
            
          int eof = inputStream.read();
          if(eof != -1) {
            System.out.println("Error: Bad format for SRTM"); 
          }
  
          inputStream.close();
        }
        catch(FileNotFoundException ex) {
          System.out.println(
              "Unable to open file '" + 
              TERRAIN_FILEPATH + "'");
        }
        catch(IOException ex) {
          System.out.println(
              "Error reading file '" +
              TERRAIN_FILEPATH + "'");
        }
      }
      /* Well terrain */
      else {
        max = 1000.0;
        min = 0.0;
        for(int i = 0; i < EAST_WIDTH; i++) {
          for(int j = 0; j < SOUTH_WIDTH; j++) {
            if(i > EAST_WIDTH/6 && i < (EAST_WIDTH - EAST_WIDTH/6) &&
               j > SOUTH_WIDTH/6 && j < (SOUTH_WIDTH - SOUTH_WIDTH/6)) {
              h[i][j] = 0.0;
            }
            else {
              h[i][j] = 1000.0;
            }
          }
        }
      } 
    }
  
    private int twosComp(int val, int bits) {
      if((val & (1 << (bits - 1))) != 0) {
        val = val - (1 << bits);
      }
      return val;
    }
  
    private boolean inBounds(int x, int y) {
      /* Check inputs */
      if(x < 0 || y < 0)
        return false;
      else if(x >= EAST_WIDTH || y >= SOUTH_WIDTH)
        return false;
      /* Check source, it is possible that x and y
       * are also the source, but it doesn't hurt to 
       * check twice.
      */
      else if(srcX < 0 || srcY < 0)
        return false;
      else if(srcX >= EAST_WIDTH || srcY >= SOUTH_WIDTH)
        return false;
      else 
        return true;
    }
  
    public double getHeight(int x, int y) {
      return h[x][y];
    }
  
    public int getSrcX() {
      return srcX;
    }
    
    public int getSrcY() {
      return srcY;
    }
  
    /* Calculates line of sight at position (x0, y0)
     * where x0 amd y0 are coordinates, not locations
     * Must be called after constructor
    */
    public void calculateLOS(int x0, int y0) {
  
      srcX = x0;
      srcY = y0;
      
      double x0f = (double) srcX;
      double y0f = (double) srcY;
     
      /* If the source is not in bounds exit
       * the default behavior is that motes outside the range
       * cannot talk to each other.
      */
      if(!inBounds(x0, y0))
        return;
      
      /* Wang, Robinson, and White's Algorithm for finding line of sight */
      double z0 = h[x0][y0];
      /* Put source on a tripod
       * z0 += 5;
       */
  
      int x1;
      int y1;
      int x2;
      int y2;
      double z1;
      double z2;
      double xf;
      double yf;
      double visible = 0;
      double actual = 0;
      
      for(int x = x0 - 1; x <= x0 + 1; x++) {
        for(int y = y0 - 1; y <= y0 + 1; y++) {
          if(x < 0 || x >= EAST_WIDTH || y < 0 || y >= SOUTH_WIDTH) {
            continue;
          }
          los[x][y] = h[x][y];
        }
      }
      
      /* Divide into 8 octets and 8 axes */
      /* E */
      for(int x = x0 + 2; x < EAST_WIDTH; x++) {
        x1 = x - 1;
        z1 = los[x1][y0];
        xf = (double) x;
        visible = (z1 - z0)*((xf - x0f)/(xf - x0f - 1)) + z0;
        actual = h[x][y0];
        los[x][y0] = (visible > actual) ? visible : actual;
      }
      /* S */
      for(int y = y0 + 2; y < SOUTH_WIDTH; y++) {
        y1 = y - 1;
        z1 = los[x0][y1];
        yf = (double) y;
        visible = (z1 - z0)*((yf - y0f)/(yf - y0f - 1)) + z0;
        actual = h[x0][y];
        los[x0][y] = (visible > actual) ? visible : actual;
      }
      /* W */
      for(int x = x0 - 2; x >= 0; x--) {
        x1 = x + 1;
        z1 = los[x1][y0];
        xf = (double) x;
        visible = (z1 - z0)*((x0f - xf)/(x0f - xf - 1)) + z0;
        actual = h[x][y0];
        los[x][y0] = (visible > actual) ? visible : actual;
      }
      /* N */
      for(int y = y0 - 2; y >= 0; y--) {
        y1 = y + 1;
        z1 = los[x0][y1];
        yf = (double) y;
        visible = (z1 - z0)*((y0f - yf)/(y0f - yf - 1)) + z0;
        actual = h[x0][y];
        los[x0][y] = (visible > actual) ? visible : actual;
      }
      /* SE */
      for(int x = x0 + 2, y = y0 + 2; x < EAST_WIDTH && y < SOUTH_WIDTH;
          x++, y++) {
        x1 = x - 1;
        y1 = y - 1;
        z1 = los[x1][y1];
        xf = (double) x;
        visible = (z1 - z0)*((xf - x0f)/(xf - x0f - 1)) + z0;
        actual = h[x][y];
        los[x][y] = (visible > actual) ? visible : actual;
      }
      /* SW */
      for(int x = x0 - 2, y = y0 + 2; x >= 0 && y < SOUTH_WIDTH;
          x--, y++) {
        x1 = x + 1;
        y1 = y - 1;
        z1 = los[x1][y1];
        xf = (double) x;
        visible = (z1 - z0)*((x0f - xf)/(x0f - xf - 1)) + z0;
        actual = h[x][y];
        los[x][y] = (visible > actual) ? visible : actual;
      }
      /* NW */
      for(int x = x0 - 2, y = y0 - 2; x >= 0 && y >= 0;
          x--, y--) {
        x1 = x + 1;
        y1 = y + 1;
        z1 = los[x1][y1];
        xf = (double) x;
        visible = (z1 - z0)*((x0f - xf)/(x0f - xf - 1)) + z0;
        actual = h[x][y];
        los[x][y] = (visible > actual) ? visible : actual;
      }
      /* NE */
      for(int x = x0 + 2, y = y0 - 2; x < EAST_WIDTH && y >= 0;
          x++, y--) {
        x1 = x - 1;
        y1 = y + 1;
        z1 = los[x1][y1];
        xf = (double) x;
        visible = (z1 - z0)*((xf - x0f)/(xf - x0f - 1)) + z0;
        actual = h[x][y];
        los[x][y] = (visible > actual) ? visible : actual;
      }
      /* E-SE */
      for(int x = x0 + 2; x < EAST_WIDTH; x++) {
        for(int y = y0 + 1; ((y - y0) < (x - x0)) && (y < SOUTH_WIDTH); y++) {
          x1 = x - 1;
          y1 = y - 1;
          z1 = los[x1][y1];
          x2 = x - 1;
          y2 = y;
          z2 = los[x2][y2];
          xf = (double) x;
          yf = (double) y;
          visible = (z1 - z0)*((yf - y0f)/(xf - x0f - 1)) 
                    + (z2 - z0)*((xf - x0f - (yf - y0f))/(xf - x0f - 1)) + z0;
          actual = h[x][y];
          los[x][y] = (visible > actual) ? visible : actual;
        }
      }
      /* S-SE */
      for(int y = y0 + 2; y < SOUTH_WIDTH; y++) {
        for(int x = x0 + 1; ((x - x0) < (y - y0)) && x < EAST_WIDTH; x++) {
          x1 = x - 1;
          y1 = y - 1;
          z1 = los[x1][y1];
          x2 = x;
          y2 = y - 1;
          z2 = los[x2][y2];
          xf = (double) x;
          yf = (double) y;
          visible = (z1 - z0)*((xf - x0f)/(yf - y0f - 1)) 
                    + (z2 - z0)*((yf - y0f - (xf - x0f))/(yf - y0f - 1)) + z0; 
          actual = h[x][y];
          los[x][y] = (visible > actual) ? visible : actual;
        }
      }
      /* S-SW */
      for(int y = y0 + 2; y < SOUTH_WIDTH; y++) {
        for(int x = x0 - 1; ((x0 - x) < (y - y0)) && (x >= 0); x--) {
          x1 = x + 1;
          y1 = y - 1;
          z1 = los[x1][y1];
          x2 = x;
          y2 = y - 1;
          z2 = los[x2][y2];
          xf = (double) x;
          yf = (double) y;
          visible = (z1 - z0)*(-(xf - x0f)/(yf - y0f - 1)) 
                    + (z2 - z0)*((xf - x0f + yf - y0f)/(yf - y0f - 1)) + z0;
          actual = h[x][y];
          los[x][y] = (visible > actual) ? visible : actual;
        }
      }
      /* W-SW */
      for(int x = x0 - 2; x >= 0; x--) {
        for(int y = y0 + 1; ((y - y0) < (x0 - x)) && y < SOUTH_WIDTH; y++) {
          x1 = x + 1;
          y1 = y - 1;
          z1 = los[x1][y1];
          x2 = x + 1;
          y2 = y;
          z2 = los[x2][y2];
          xf = (double) x;
          yf = (double) y;
          visible = (z1 - z0)*(-(yf - y0f)/(xf - x0f + 1))
                    + (z2 - z0)*((xf - x0f + yf - y0f)/(xf - x0f + 1)) + z0;
          actual = h[x][y];
          los[x][y] = (visible > actual) ? visible : actual;
        }
      }
      /* W-NW */
      for(int x = x0 - 2; x >= 0; x--) {
        for(int y = y0 - 1; ((y0 - y) < (x0 - x)) && y >= 0; y--) {
          x1 = x + 1;
          y1 = y + 1;
          z1 = los[x1][y1];
          x2 = x + 1;
          y2 = y;
          z2 = los[x2][y2];
          xf = (double) x;
          yf = (double) y;
          visible = (z1 - z0)*((yf - y0f)/(xf - x0f + 1))
                    + (z2 - z0)*((xf - x0f - (yf - y0f))/(xf - x0f + 1)) + z0;
          actual = h[x][y];
          los[x][y] = (visible > actual) ? visible : actual;
        }
      }
      /* N-NW */
      for(int y = y0 - 2; y >= 0; y--) {
        for(int x = x0 - 1; ((x0 - x) < (y0 - y)) && (x >= 0); x--) {
          x1 = x + 1;
          y1 = y + 1;
          z1 = los[x1][y1];
          x2 = x;
          y2 = y + 1;
          z2 = los[x2][y2];
          xf = (double) x;
          yf = (double) y;
          visible = (z1 - z0)*((xf - x0f)/(yf - y0f + 1))
                    + (z2 - z0)*((yf - y0f - (xf - x0f))/(yf - y0f + 1)) + z0;
          actual = h[x][y];
          los[x][y] = (visible > actual) ? visible : actual;
        }
      }
      /* N-NE */
      for(int y = y0 - 2; y >= 0; y--) {
        for(int x = x0 + 1; (x - x0 < y0 - y) && (x < EAST_WIDTH); x++) {
          x1 = x - 1;
          y1 = y + 1;
          z1 = los[x1][y1];
          x2 = x;
          y2 = y + 1;
          z2 = los[x2][y2];
          xf = (double) x;
          yf = (double) y;
          visible = (z1 - z0)*(-(xf - x0f)/(yf - y0f + 1))
                    + (z2 - z0)*((xf - x0f + yf - y0f)/(yf - y0f + 1)) + z0;
          actual = h[x][y];
          los[x][y] = (visible > actual) ? visible : actual;
        }
      }
      /* E-NE */
      for(int x = x0 + 2; x < EAST_WIDTH; x++) {
        for(int y = y0 - 1; (y0 - y < x - x0) && (y >= 0); y--) {
          x1 = x - 1;
          y1 = y + 1;
          z1 = los[x1][y1];
          x2 = x - 1;
          y2 = y;
          z2 = los[x2][y2];
          xf = (double) x;
          yf = (double) y;
          visible = (z1 - z0)*(-(yf - y0f)/(xf - x0f - 1))
                    + (z2 - z0)*((xf - x0f + yf - y0f)/(xf - x0f - 1)) + z0;
          actual = h[x][y];
          los[x][y] = (visible > actual) ? visible : actual;
        }
      }
    }
  
    public int convertLocToCord(int loc) {
      int cord;
  
      cord = loc / 33;
  
      return cord;
    }
  
    /* Using the srcX and srcY location determines whether the giben destination
     * is in LOS, where destX and destY are coordinates
    */
    public boolean isThereLOS(int dst_x, int dst_y) {
    
      /* If the destination or source is not in bounds
       * then the default behavour is that motes cannot 
       * talk to each other.
      */
      if(!inBounds(dst_x, dst_y))
        return false;
  
      if(h[dst_x][dst_y] >= los[dst_x][dst_y])
        return true;
      else
        return false;
    }
   
  }

}
