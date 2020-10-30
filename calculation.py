def cal_hist_auc(arrays, bins = 500):
    """Calculate the AUC of the arrays distribution
    """
    y_score = np.array(arrays)
    hist = arrays.value_counts(bins=bins)
    hist = hist.sort_index()
    append_right = hist.index[bins-1].right
    hist.index = hist.index.left
    # bins is the regions, like [1100, 1200, 1300 ...]
    bins = np.asarray(hist.index)
    # bins[0] = bins[1] - np.diff(bins)[1]
    bins = np.append(bins, append_right)
    # values is the height of each bins, like [0, 0, 1, 2, 0, 1 ...]
    values = np.asarray(hist.values)
    area = sum(np.diff(bins)*values)
    return area, bins, values

def find_bin_idx_of_value(bins, value):
    """Finds the bin which the value corresponds to."""
    array = np.asarray(value)
    idx = np.digitize(array, bins)
    if idx == 0:
        return 0
    return idx-1

def area_after_val(values, bins, val):
    """Calculates the area of the hist after a certain value"""
    left_bin_edge_index = find_bin_idx_of_value(bins, val)
#     bin_width = np.diff(bins)[1]
#     print(bin_width)
    area = sum(np.diff(bins)[left_bin_edge_index:] * values[left_bin_edge_index:])
    return area

def cal_p(fg_value, bg_area, bg_bins, bg_values):
    pvalue = area_after_val(bg_values, bg_bins, fg_value)/bg_area
    if pvalue > 1:
        pvalue = 1.0
    return pvalue

def cal_fc(fg_value, bg_mean):
    if bg_mean * fg_value > 0: # if mean and value are opposite
        fc = fg_value / bg_mean
    elif bg_mean == 0:
        fc = fg_value
    else:
        fc = bg_mean / (bg_mean - fg_value)
    return fc

# calculate p value by area at the right of curve
# calculate fc by value / background average
def cal_p_and_fc(fg_table, bg_table):
    print('INFO {time}, chunk calculation ...'.format(time=datetime.now()))
    result_table_p = fg_table.copy()
    result_table_fc = fg_table.copy()
    for factor in fg_table.index:
        factor_bg = bg_table.loc[factor,:]
        bg_mean = np.mean(factor_bg)
        bg_std = np.std(factor_bg)
        result_table_p.loc[factor,:] = fg_table.loc[factor,:].apply(sp.stats.norm.cdf, args=(bg_mean, bg_std))
        result_table_fc.loc[factor,:] = fg_table.loc[factor,:].apply(cal_fc, **{'bg_mean': bg_mean})
    print('INFO {time}, chunk finished !'.format(time=datetime.now()))
    return [1-result_table_p, result_table_fc]

def cal_p_and_fc_batch(fg_table, bg_table, n_cores=8):
    print("INFO {time}, Calculating enrichment and fold change, divide into {n} chunks...".format(time=datetime.now(), n=n_cores))
    fg_table_split = np.array_split(fg_table, n_cores)
    args = [[table, bg_table] for table in fg_table_split]
    with Pool(n_cores) as p:
        result = p.starmap(cal_p_and_fc, args)
    print("INFO {time}, Generating P value table ...".format(time=datetime.now()))
    result_table_p = pd.concat([i[0] for i in result])
    print("INFO {time}, Generating FC value table ...".format(time=datetime.now()))
    result_table_fc = pd.concat([i[1] for i in result])
    print('INFO {time}, Finished calculation enrichment and fold change!'.format(time=datetime.now()))
    return result_table_p, result_table_fc

def correct_pvalues_for_multiple_testing(pvalues, correction_type = "Benjamini-Hochberg"):                
    """                                                                                                   
    consistent with R - print correct_pvalues_for_multiple_testing([0.0, 0.01, 0.029, 0.03, 0.031, 0.05, 0.069, 0.07, 0.071, 0.09, 0.1]) 
    derive from https://stackoverflow.com/questions/7450957/how-to-implement-rs-p-adjust-in-python/7453313
    """
    pvalues = np.array(pvalues) 
    n = float(pvalues.shape[0])     
    new_pvalues = np.empty(n)
    if correction_type == "Bonferroni":   
        new_pvalues = n * pvalues
    elif correction_type == "Bonferroni-Holm": 
        values = [(pvalue, i) for i, pvalue in enumerate(pvalues)]                                      
        values.sort()
        for rank, vals in enumerate(values):                                                              
            pvalue, i = vals
            new_pvalues[i] = (n-rank) * pvalue                                                            
    elif correction_type == "Benjamini-Hochberg":                                                         
        values = [(pvalue, i) for i, pvalue in enumerate(pvalues)]                                      
        values.sort()
        values.reverse()
        new_values = []
        for i, vals in enumerate(values): 
            rank = n - i
            pvalue, index = vals 
            new_values.append((n/rank) * pvalue) 
        for i in range(0, int(n)-1): 
            if new_values[i] < new_values[i+1]:                                                           
                new_values[i+1] = new_values[i]                                                           
        for i, vals in enumerate(values):
            pvalue, index = vals
            new_pvalues[index] = new_values[i]                                                                                                                  
    return new_pvalues