//
//  UIColor.swift
//  SmartCase
//
//  Created by Squareroot on 13/07/18.
//  Copyright © 2018 Squareroot. All rights reserved.
//

import Foundation

extension UIColor {

    func toHexString() -> String {
        var r:CGFloat = 0
        var g:CGFloat = 0
        var b:CGFloat = 0
        var a:CGFloat = 0
        
        getRed(&r, green: &g, blue: &b, alpha: &a)
        
        let rgb:Int = (Int)(r*255)<<16 | (Int)(g*255)<<8 | (Int)(b*255)<<0
        
        return String(format:"#%06x", rgb)
    }
}
