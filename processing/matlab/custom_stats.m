function stats = custom_stats(discharge, yr, mo, dy, da_mi2)
% Compute the 12 custom seasonal hydrological statistics not in MHIT.
%
% Inputs:
%   discharge  - Nx1 double, daily streamflow (cfs)
%   yr         - Nx1 double, year
%   mo         - Nx1 double, month (1-12)
%   dy         - Nx1 double, day of month
%   da_mi2     - scalar drainage area (square miles); NaN if unavailable
%
% Returns struct with fields:
%   lf1, spr_dur3, spr_dur7, sum_dur3, sum_dur7,
%   spr_freq, sum_freq, spr_mag, sum_cv, sum_mag,
%   spr_ord, sum_ord

    % Initialize all outputs to NaN
    stats.lf1      = NaN;
    stats.spr_dur3 = NaN;
    stats.spr_dur7 = NaN;
    stats.sum_dur3 = NaN;
    stats.sum_dur7 = NaN;
    stats.spr_freq = NaN;
    stats.sum_freq = NaN;
    stats.spr_mag  = NaN;
    stats.sum_cv   = NaN;
    stats.sum_mag  = NaN;
    stats.spr_ord  = NaN;
    stats.sum_ord  = NaN;

    discharge = discharge(:);
    yr        = yr(:);
    mo        = mo(:);
    dy        = dy(:);

    years = unique(yr);
    nyrs  = numel(years);

    % --- LF1: median days/yr below 0.1 cfs/mi2 threshold ---
    if ~isnan(da_mi2) && da_mi2 > 0
        threshold = 0.1 * da_mi2;
        days_below = zeros(nyrs, 1);
        for i = 1:nyrs
            mask = yr == years(i);
            days_below(i) = sum(discharge(mask) < threshold, 'omitnan');
        end
        stats.lf1 = nanmedian(days_below);
    end

    % --- Moving average helpers for spring and summer ---
    spr_max3 = NaN(nyrs, 1);
    spr_max7 = NaN(nyrs, 1);
    sum_min3 = NaN(nyrs, 1);
    sum_min7 = NaN(nyrs, 1);

    for i = 1:nyrs
        % Spring: April-June
        spr_mask = yr == years(i) & mo >= 4 & mo <= 6;
        q_spr = discharge(spr_mask);
        q_spr = q_spr(~isnan(q_spr));
        if numel(q_spr) >= 3
            spr_max3(i) = max(movmean(q_spr, 3));
        end
        if numel(q_spr) >= 7
            spr_max7(i) = max(movmean(q_spr, 7));
        end

        % Summer: July-September
        sum_mask = yr == years(i) & mo >= 7 & mo <= 9;
        q_sum = discharge(sum_mask);
        q_sum = q_sum(~isnan(q_sum));
        if numel(q_sum) >= 3
            sum_min3(i) = min(movmean(q_sum, 3));
        end
        if numel(q_sum) >= 7
            sum_min7(i) = min(movmean(q_sum, 7));
        end
    end
    stats.spr_dur3 = nanmedian(spr_max3);
    stats.spr_dur7 = nanmedian(spr_max7);
    stats.sum_dur3 = nanmedian(sum_min3);
    stats.sum_dur7 = nanmedian(sum_min7);

    % --- Frequency thresholds from full record ---
    q_clean = discharge(~isnan(discharge));
    if numel(q_clean) < 2
        return
    end
    p10 = prctile(q_clean, 10);
    p90 = prctile(q_clean, 90);

    % SPR_FREQ: Apr-Jun events above 10th percentile; median count/yr
    spr_ev = NaN(nyrs, 1);
    for i = 1:nyrs
        mask = yr == years(i) & mo >= 4 & mo <= 6;
        q = discharge(mask);
        above = q > p10;
        above(isnan(q)) = false;
        trans = diff([0; above; 0]);
        spr_ev(i) = sum(trans == 1);
    end
    stats.spr_freq = nanmedian(spr_ev);

    % SUM_FREQ: Jul-Sep events below 90th percentile; median count/yr
    sum_ev = NaN(nyrs, 1);
    for i = 1:nyrs
        mask = yr == years(i) & mo >= 7 & mo <= 9;
        q = discharge(mask);
        below = q < p90;
        below(isnan(q)) = false;
        trans = diff([0; below; 0]);
        sum_ev(i) = sum(trans == 1);
    end
    stats.sum_freq = nanmedian(sum_ev);

    % --- Magnitude / drainage-area normalized ---
    if ~isnan(da_mi2) && da_mi2 > 0
        spr_max_vals = NaN(nyrs, 1);
        sum_min_vals = NaN(nyrs, 1);
        for i = 1:nyrs
            spr_mask = yr == years(i) & mo >= 4 & mo <= 6;
            spr_max_vals(i) = nanmax(discharge(spr_mask));
            sum_mask = yr == years(i) & mo >= 7 & mo <= 9;
            sum_min_vals(i) = nanmin(discharge(sum_mask));
        end
        stats.spr_mag = nanmedian(spr_max_vals / da_mi2);
        stats.sum_mag = nanmedian(sum_min_vals / da_mi2);
    end

    % SUM_CV: median of annual CV for summer (Jul-Sep)
    sum_cv_vals = NaN(nyrs, 1);
    for i = 1:nyrs
        mask = yr == years(i) & mo >= 7 & mo <= 9;
        q = discharge(mask);
        q = q(~isnan(q));
        if numel(q) > 1 && mean(q) ~= 0
            sum_cv_vals(i) = std(q) / mean(q) * 100;
        end
    end
    stats.sum_cv = nanmedian(sum_cv_vals);

    % --- Timing: Julian day helpers ---
    days_per_month = [31 28 31 30 31 30 31 31 30 31 30 31];
    cum_days = [0, cumsum(days_per_month(1:11))];  % month offset (1-indexed: cum_days(m) = days before month m)

    % SPR_ORD: Julian date of spring (Apr-Jun) max; median over calendar years
    spr_jday = NaN(nyrs, 1);
    for i = 1:nyrs
        mask = yr == years(i) & mo >= 4 & mo <= 6;
        if ~any(mask), continue; end
        q = discharge(mask);
        d = dy(mask);
        m = mo(mask);
        [qmax, idx] = max(q);
        if ~isnan(qmax)
            spr_jday(i) = cum_days(m(idx)) + d(idx);
        end
    end
    stats.spr_ord = nanmedian(spr_jday);

    % SUM_ORD: Julian date of summer (Jul-Sep) min; median over water years
    water_yr = yr - (mo <= 9);
    wyrs = unique(water_yr);
    sum_jday = NaN(numel(wyrs), 1);
    for i = 1:numel(wyrs)
        mask = water_yr == wyrs(i) & mo >= 7 & mo <= 9;
        if ~any(mask), continue; end
        q = discharge(mask);
        d = dy(mask);
        m = mo(mask);
        [qmin, idx] = min(q);
        if ~isnan(qmin)
            sum_jday(i) = cum_days(m(idx)) + d(idx);
        end
    end
    stats.sum_ord = nanmedian(sum_jday);
end
