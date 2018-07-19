% energy harvester size
% x = [0.5, 1, 5, 10, 20, 50]  % 100, 1000,10000] 
x = [0.5, 0.7, 0.9, 1, 2, 3, 5, 7, 9, 10, 14, 18, 20, 30, 40, 50]
%     70, 90, 100, 400, 700, 1000, 4000, 7000, 10000, 20000, 30000]

% solar panel size
% y = [0.1, 1, 2, 5, 10, 25] %, 50, 100, 250]
  y = [0.1, 0.4, 0.7, 1, 1.5, 1.7, 2, 3, 4, 5, 7, 9, 10, 15, 20, 25]
%   , 35, 45, 50, 70, 90, 100, 150, 200, 250, 300, 350] 

% fulfillment percentage for the LESS method
% z = [30.88, 44.30, 68.77, 100.0, 100.0, 100.0] %, 100.0, 100.0, 100.0]
  z = [30.905, 36.85, 41.205, 44.34, 52.67, 59.3225, 68.8075, 87.2025, 99.31, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]

x = x';
y = y';
z = z';

[x_3d,y_3d,z_3d] = vecsurf(x,y,z,'MosaicPicture');

figure
% surf(x_3d,y_3d,z_3d)
surf(x_3d,y_3d,z_3d)
zlim([0, 150])

set(gcf,'color','w');
set(gca,'xcol','black','ycol','black')
set(gca, 'FontName', 'Fira Code')
set(gca, 'GridAlpha', 1.)

xlabel({'Sol. panel'; 'size (cm^2)'})
ylabel({'Bat. size'; '(mAh)'})
zlabel('% OP met (LESS)')

colormap(parula)
% colormap(hot(256))
% colormap(jet(256))
colorbar EastOutside
camlight right
lighting phong
