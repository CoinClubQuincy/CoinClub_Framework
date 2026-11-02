//
//  Card+CoreDataProperties.swift
//  
//
//  Created by Squareroot on 29/08/18.
//
//

import Foundation
import CoreData


extension Card {

    @nonobjc public class func fetchRequest() -> NSFetchRequest<Card> {
        return NSFetchRequest<Card>(entityName: "Card")
    }

    @NSManaged public var cardColor: String?
    @NSManaged public var cardImage: NSData?
    @NSManaged public var cardName: String?
    @NSManaged public var id: String?
    @NSManaged public var isUpdate: Bool

}
