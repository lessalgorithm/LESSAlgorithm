
% energy harvester size
solar_panel_size = [0.5, 1, 5, 10, 20, 50]  % 100, 1000,10000] 

% solar panel size
battery_size = [0.1, 1, 2, 5, 10, 25] %, 50, 100, 250]

% fulfillment percentage for the LESS method
less_fulfillment_per = [30.88, 44.30, 68.77, 100.0, 100.0, 100.0] %, 100.0, 100.0, 100.0]

figure1 = figure;

x=solar_panel_size;
y=battery_size;
z=less_fulfillment_per;

tri = delaunay(x,y);
trisurf(tri,x,y,z)

% dx=1;
% dy=1;

% x_edge=[floor(min(x)):dx:ceil(max(x))];
% y_edge=[floor(min(y)):dy:ceil(max(y))];
% [X,Y]=meshgrid(x_edge,y_edge);
% Z=griddata(x,y,z,X,Y);
% The following line of code is if you use JE's gridfit:
% Z=gridfit(x,y,z,x_edge,y_edge);

%NOW surf and mesh will work...

% surf(X,Y,Z)
% mesh(X,Y,Z)

% dx=0.5;
% dy=0.5;
% 
% x_edge = [floor(min(x)):dx:ceil(max(x))];
% y_edge = [floor(min(y)):dy:ceil(max(y))];
% 
% [X,Y] = meshgrid(x_edge,y_edge);
% 
% [zgrid,xgrid,ygrid] =gridfit(x,y,z,x_edge,y_edge);
% 
% disp(size(xgrid))
% disp(size(ygrid))
% disp(size(zgrid))
% 
% surf(xgrid, ygrid, zgrid);
% surf(x_edge, y_edge, g);


camlight right;
lighting phong;
shading interp
line(x,y,z,'marker','.','markersize', 4,'linestyle', 'none');
title 'Use topographic contours to recreate a surface'

% [qx,qy] = meshgrid(linspace(min(x),max(x)),linspace(min(y),max(y)));
% F = TriScatteredInterp(x,y,z);
% qz = F(qx,qy);
% surf(qx,qy,qz,'FaceColor','interp')

% [X,Y] = meshgrid(x_edge,y_edge);
% [X,Y] = meshgrid(x, y);
% 
% Z=griddata(x, y, z, X, Y);
% 
% surf(X,Y,Z, 'FaceColor','interp')
