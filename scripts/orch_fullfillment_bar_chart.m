axes1 = axes('Parent',figure);
grid on

width = 1;
figure(1); 
hold on;

locationDatasets = {'1523100011_TORTotal_solartracking_results.json', 
                    '1523099980_NYCTotal_solartracking_results.json', 
                    '1523100045_HTITotal_solartracking_results.json'}

for location=1:3
    xval=location;    
    
    vector = getPredOrchFullfilmentForLocation(locationDatasets{location});
    x=linspace(1, 4, size(vector, 1));
%     x=linspace(1, 4, size(vector, 1));
    
    h = bar3(x, vector, width, 'grouped')
    Xdat = get(h,'Xdata');
    for ii=1:length(Xdat)
        Xdat{ii}=Xdat{ii}+(xval-1)*ones(size(Xdat{ii}));
        set(h(ii),'XData',Xdat{ii});
    end    
    
    set(h(1),'facecolor',1/255*[0, 179, 179]);
    set(h(2),'facecolor',1/255*[51, 153, 255]);
%     set(h(2),'facecolor',1/255*[204, 102, 0]);
%     set(h(3),'facecolor',1/255*[51, 153, 255]);
%     set(h(4),'facecolor',1/255*[249, 188, 6]);
    set(h(3),'facecolor',1/255*[249, 188, 6]);
    
    if(location == 3)
%         legend([h(1) h(2) h(3) h(4)],{'static', 'orchestrator', 'ENO baseline', 'LESS', 'target'});
        legend([h(1) h(2) h(3) ],{'static', 'ENO-baseline', 'LESS'});
    end
end
                
% xlim([0 3]);
view(3);

set(gcf,'color','w');
set(gca,'xcol','black','ycol','black')
set(gca,'FontName', 'Fira Code')
set(gca,'GridAlpha', 1.)

xlabel('location')
ylabel('month')
zlabel('% OP met')

set(axes1,'YTick',[1 2 3 4],'YTickLabel',...
    {'jan-march','april-june','jul-sep','oct-dec'});

set(axes1,'XTick',[1 2 3 4],'XTickLabel',...
     {'Toronto','New York','Haiti'});

% view(axes1,[-134.09006752598 66.1729713465918]);
view(axes1,[152.30993247402 60.4]);
% view(axes1,[162.30993247402 51.6]);
 
function orchFullfilment = getPredOrchFullfilmentForLocation(jsonFile)
    fname = jsonFile; 
    fid = fopen(fname); 
    raw = fread(fid,inf);
    str = char(raw');
    fclose(fid);
    val = jsondecode(str);
                   %                   static             orchas               eno                less
%     orchFullfilment = [[val(1).orchFullfilment, val(5).orchFullfilment, val(9).orchFullfilment, val(13).orchFullfilment],
%                        [val(2).orchFullfilment, val(6).orchFullfilment, val(10).orchFullfilment, val(14).orchFullfilment],
%                        [val(3).orchFullfilment, val(7).orchFullfilment, val(11).orchFullfilment, val(15).orchFullfilment],
%                        [val(4).orchFullfilment, val(8).orchFullfilment, val(12).orchFullfilment, val(16).orchFullfilment]];
                   
    orchFullfilment = [[val(1).orchFullfilment, val(9).orchFullfilment, val(13).orchFullfilment],
                       [val(2).orchFullfilment, val(10).orchFullfilment, val(14).orchFullfilment],
                       [val(3).orchFullfilment, val(11).orchFullfilment, val(15).orchFullfilment],
                       [val(4).orchFullfilment, val(12).orchFullfilment, val(16).orchFullfilment]];
end